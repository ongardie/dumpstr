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

from django import http
from django.shortcuts import render_to_response
from django.template import RequestContext

import settings

def get_setting(name, default=''):
    """Return a setting or a default it if was not set."""

    try:
        return getattr(settings, name)
    except AttributeError:
        return default

def context_processor(request):
    """Called when each RequestContext is created to create common
    variables for templates."""

    context = {}
    return {'WWW_ROOT': get_setting('WWW_ROOT'),
            'STATIC_URL': get_setting('STATIC_URL'),
            'PROJECT': get_setting('PROJECT')}


def home(request):
    """The view that is called on the front page of the application."""

    return render_to_response('home.html',
                              {},
                              RequestContext(request))
