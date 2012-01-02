=====
About
=====

This is the README file for the dumpstr project. A dumpstr installation
provides a place for you to upload and view simple reports.

=======
License
=======

Copyright (c) 2011 Stanford University

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR(S) DISCLAIM ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL AUTHORS BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

=====
Dumpy
=====

Dumpy is the logo for dumpstr. It was created by Matt Melvin of
http://mattmelvin.com and is used in dumpstr with his permission. Matt would
prefer uses of dumpy in dumpstr to link to mattmelvin.com . For more
information, see the dumpy/README file.

============
Installation
============

Django
------

You need django to run dumpstr.
On Debian, you can install the package python-django.

Static Files
------------

Underneath ``static/``, you need to create the following on debian:

- a file named ``jquery.js`` containing the jquery javascript library
- a file named ``jquery.cookie.js`` containing the cookie plugin for jquery
- a directory named ``fancybox`` containing the fancybox javascript library
- a directory named ``flot`` containing the flot javascript library
- a directory named ``admin`` containing contrib/admin/media from django

On Debian Wheezy, you can run the following commands from your static directory::

  sudo apt-get install libjs-jquery libjs-jquery-fancybox \
                       libjs-flot libjs-jquery-cookie
  ln -s /usr/share/javascript/jquery/jquery.js jquery.js
  ln -s /usr/share/javascript/jquery-cookie/jquery.cookie.js jquery.cookie.js
  ln -s /usr/share/javascript/jquery-fancybox fancybox
  ln -s /usr/share/javascript/flot flot
  ln -s /usr/share/pyshared/django/contrib/admin/media admin

Settings
--------

You should set the following settings in a file called ``local_settings.py``:

- HOME_TRENDS:
    This is a list of trend IDs (strings) of trends that should be shown on the
    home page. It defaults to ['test'], which is also fine for starters.
- PROJECT:
    Set this to a short word or phrase that describes your installation. This
    will end up in the top navigation bar.
- STATIC_URL:
    This is the HTTP-accessible URL for the static files. It must have a
    trailing slash.
- WWW_ROOT:
    This is prepended to all URLs in the application. It must have a trailing
    and leading slash.

The following settings should be overridden as in any Django application. Refer
to https://docs.djangoproject.com/en/dev/ref/settings/ for documentation.

- SECRET_KEY
- DATABASES
- TEMPLATE_DIRS

Database
--------

To create your database, run::

  python manage.py syncdb

dumpstr is known to work with SQLite.


=================
Uploading Reports
=================

There is a file named ``upload.py`` in this directory that can be used to
upload new reports over HTTP. This file may be copied to other directories or
hosts and used from there -- it does not depend on any other files.

Most of a report is specified as a JSON-formatted *report* object.
Additionally, each report can specify *trends*, graphs that it should be
plotted on.

report
    A list of sections.

section
    An object with the following attributes:
        - ``key`` is a string used to look up a human-readable label for the
          section.
        - ``lines`` is a list of *line*\s.

line
    An object with the following attributes:
        - ``key`` is a string used to look up a human-readable label for the
          line.
        - ``summary`` is a number, string, or list of strings that describes
          the points (for example, the average, min, and max).
        - ``points`` is a number, string, or list of *point*\s.
        - ``unit`` is a short, human-readable description of the units used in
          ``points``.

point
    A tuple consisting of:
        - a string serving as a label on the graphs
        - a number specifying the value to plot

trends
    A list of tuples consisting of:
        - a string identifying the trend
        - a number specifying the value to plot
