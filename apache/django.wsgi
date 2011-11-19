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

# This file is called by apache to serve dynamic content from the dumpstr
# application. See http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
# for more information.

import django.core.handlers.wsgi
import sys
import os

parent = os.path.dirname

# path should automatically point above your dumpstr root directory
path = parent(parent(parent(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'dumpstr.settings'

_application = django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
    if environ['PATH_INFO'] == '':
        environ['PATH_INFO'] = '/'
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    return _application(environ, start_response)

# The following can be useful for testing WSGI:
# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     yield 'Hello World\n'
