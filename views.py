# Copyright (c) 2011 Stanford University
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR(S) DISCLAIM ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL AUTHORS BE
# LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
# ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

# This file contains the various views used in the webmetrics
# application.

from __future__ import division

import datetime
import itertools
import json
import re
import time

from django import http
from django.db import connection, transaction, DatabaseError
from django.middleware import csrf
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

import models
import settings

def get_setting(name, default=''):
    """Return a setting or a default it if was not set."""

    try:
        return getattr(settings, name)
    except AttributeError:
        return default

def make_trend_table_name(trend_id):
    """Make sure the trend_id is alphanumeric and return its
    corresponding database table."""

    if re.search('^[A-Za-z0-9_]+$', trend_id) is None:
        raise ValueError('Trends must be alphanumeric: ' + trend_id)
    return 'webmetrics_trends_' + trend_id


def context_processor(request):
    """Called when each RequestContext is created to create common
    variables for templates."""

    # This is a hack to get the CSRF cookie to be sent to the client on every
    # request.
    csrf.get_token(request)

    latest_reports = (models.Report.objects.values('id', 'owner', 'type')
                        .order_by('-id')[:10])
    try:
        latest_report = latest_reports[0]
    except IndexError:
        latest_report = None
    return {
        'WWW_ROOT': get_setting('WWW_ROOT'),
        'STATIC_URL': get_setting('STATIC_URL'),
        'PROJECT': get_setting('PROJECT'),
        'latest_reports': latest_reports,
        'latest_report': latest_report,
    }

def make_key(*components):
    return '#'.join(components)

def get_description(*components):
    try:
        descr = (models.Description.objects.filter(key=make_key(*components))
                    .order_by('-id')[0])
    except IndexError:
        return (components[-1], '')
    else:
        return (descr.label, descr.descr)

def get_trends(trend_ids):
    """Given a list of trend_ids, return a list of trend objects for templates
    to use."""
    trends = []
    for trend_id in trend_ids:
        label, desc = get_description('trend', trend_id)
        trends.append({
            'id': trend_id,
            'key': make_key('trend', trend_id),
            'label': label,
            'description': desc,
            # json handles multi-line strings
            'json_description': json.dumps(desc),
        })
    return trends


# Regular views

def home(request):
    """The view that is called on the front page of the application."""

    return render_to_response('home.html',
                              {'trends': get_trends(
                                    get_setting('HOME_TRENDS', ['test']))},
                              RequestContext(request))

def view_report(request, report_id):
    """A detailed view of a report."""

    ids = itertools.count()

    report = models.Report.objects.get(id=int(report_id))
    if report.data:
        doc = json.loads(report.data)
    else:
        doc = []
    if report.trends:
        trend_ids = [trend_id for trend_id, value in json.loads(report.trends)]
        trends = get_trends(trend_ids)
    else:
        trends = []

    sections = []
    for section in doc:
        lines = []
        for line in section['lines']:
            line_id = '%d' % next(ids)
            raw_points = line['points']
            if type(raw_points) is list:
                if len(raw_points) == 0:
                    continue
                points = []
                default_label_iter = itertools.count()
                for point in raw_points:
                    try:
                        label, point = point
                    except TypeError:
                        label = str(default_label_iter.next())
                    assert type(point) in [int, float]
                    points.append((label, point))
                json_points = json.dumps(points)
            else:
                point = raw_points
                json_points = 'null'
            label, note = get_description(
                            report.type,
                            section['key'],
                            line['key'])
            lines.append({'id': line_id,
                          # TODO 'indent_level': ' ' * line['key'].count(' '),
                          'key': make_key(report.type, section['key'],
                                          line['key']),
                          'label': label,

                          # json handles multi-line strings
                          'json_note': json.dumps(note),

                          'json_summary': json.dumps(line['summary']),
                          'json_points': json_points,
                          'unit': line['unit'],
                         })
        title, descr = get_description(
                        report.type, section['key'])
        sections.append({'key': make_key(report.type, section['key']),
                         'title': title,

                          # json handles multi-line strings
                         'json_description': json.dumps(descr),

                         'lines': lines})
    return render_to_response('report.html',
                              {'sections': sections,
                               'report': report,
                               'report_datetime': datetime.datetime.fromtimestamp(report.timestamp),
                               'trends': trends},

                              RequestContext(request))

def view_latest_report(request):
    latest_id = models.Report.objects.values('id').order_by('-id')[0]['id']
    return view_report(request, latest_id)


# AJAX views

def post_description(request):
    """Called to save labels and descriptions."""

    if request.method != 'POST':
        return http.HttpResponse('Status 405: Method Not Allowed',
                                 status=405)
    # This intentionally adds a row to the database rather than overwriting a
    # row as a dumb form of version control; see the Description class for more
    # info.
    descr = models.Description(key=request.POST['key'],
                               label=request.POST['label'],
                               descr=request.POST['description'])
    descr.save()
    return http.HttpResponse()

@csrf_exempt
@transaction.commit_manually
def post_report(request):
    """Called from an external application to upload a new report."""

    try:
        if request.method != 'POST':
            return http.HttpResponse('Status 405: Method Not Allowed',
                                     status=405)

        # Minimally sanitize data
        if request.POST['data']:
            json.loads(request.POST['data'])

        # Sanitize trends
        trends = []
        if request.POST['trends']:
            for trend_id, point in json.loads(request.POST['trends']):
                trends.append((make_trend_table_name(trend_id),
                               float(point)))

        # Save the report
        report = models.Report(type=request.POST['type'],
                               owner=request.POST['owner'],
                               timestamp=time.time(),
                               data=request.POST['data'],
                               trends=request.POST['trends'])
        report.save()

        # Add any trend points
        cursor = connection.cursor()
        for table, point in trends:
            def attempt():
                cursor.execute('INSERT INTO ' + table +
                        '(timestamp, point, report_id) '
                        'VALUES (%s, %s, %s)',
                        [time.time(), point, report.id])
            try:
                attempt()
            except DatabaseError:
                cursor.execute('CREATE TABLE ' + table + """(
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "timestamp" INTEGER NOT NULL,
                    "point" NUMERIC NOT NULL,
                    "report_id" INTEGER)""")
                attempt()
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()
        return http.HttpResponse(report.id)

def get_trend(request, trend_id):
    """Returns the data for a trend graph."""

    start = None
    end = None
    if 'from' in request.GET and 'to' in request.GET:
        start = float(request.GET['from'])
        end = float(request.GET['to'])

    cursor = connection.cursor()
    table = make_trend_table_name(trend_id)

    if start is None:
        cursor.execute('SELECT COUNT(*) FROM ' + table)
    else:
        cursor.execute('SELECT COUNT(*) FROM ' + table +
                       ' WHERE id >= %s AND id <= %s',
                       [start, end])

    num_lines = cursor.fetchone()[0]
    skip_per_point = max(num_lines // 1000 - 1, 1)

    if start is None:
        cursor.execute('SELECT id, point, timestamp, report_id'
                       ' FROM ' + table +
                       ' WHERE id %% %s == 0'
                       ' ORDER BY id',
                       [skip_per_point])
    else:
        cursor.execute('SELECT id, point, timestamp, report_id'
                       ' FROM ' + table +
                       ' WHERE id >= %s AND id <= %s'
                       ' AND id %% %s == 0'
                       ' ORDER BY id',
                       [start, end, skip_per_point])
    trend = cursor.fetchall()
    response = json.dumps(trend)

    return http.HttpResponse(response)
