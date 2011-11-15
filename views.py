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

    context = {}
    return {'WWW_ROOT': get_setting('WWW_ROOT'),
            'STATIC_URL': get_setting('STATIC_URL'),
            'PROJECT': get_setting('PROJECT')}

def make_key(*components):
    return '#'.join(components)

def get_description(*components):
    try:
        descr = models.Description.objects.get(key=make_key(*components))
    except models.Description.DoesNotExist:
        return (components[-1], '')
    else:
        return (descr.label, descr.descr)

# Regular views

def home(request):
    """The view that is called on the front page of the application."""

    return render_to_response('home.html',
                              {},
                              RequestContext(request))

def view_report(request, report_id):
    """A detailed view of a report."""

    ids = itertools.count()

    report = models.Report.objects.get(id=int(report_id))
    if report.data:
        doc = json.loads(report.data)
    else:
        doc = []

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
                          'note': note,
                          'json_summary': json.dumps(line['summary']),
                          'json_points': json_points,
                          'unit': line['unit'],
                         })
        title, descr = get_description(
                        report.type, section['key'])
        sections.append({'key': make_key(report.type, section['key']),
                         'title': title,
                         'description': descr,
                         'lines': lines})
    return render_to_response('report.html',
                              {'sections': sections,
                               'report': report,
                               'report_datetime': datetime.datetime.fromtimestamp(report.timestamp)},
                              RequestContext(request))

# AJAX views

def post_description(request):
    """Called to save labels and descriptions."""

    if request.method != 'POST':
        return http.HttpResponse('Status 405: Method Not Allowed',
                                 status=405)
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
