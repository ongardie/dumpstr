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

# This file defines the database models used in the webmetrics application.

from django.db import models

class Report(models.Model):
    """Users submit reports consiting of measurements that they have collected
    for a particular event."""

    # The human-readable type of the event that was measured.
    type = models.CharField(max_length=65535)

    # The name of the user who submitted the report.
    owner = models.CharField(max_length=65535)

    # A UNIX timestamp of when the report was submitted.
    timestamp = models.IntegerField()

    # A JSON object containing the measurements in the report.
    data = models.TextField()

    # A JSON object containing a list of pairs, each having a name of a trend
    # line and a point value which this report contributes.
    trends = models.TextField()

class Description(models.Model):
    """A label and a description for some key. These are stored in the database
    so that users can modify them easily.

    The id field is created automatically by Django. It serves as a version
    number for rows, so the current label and description for a key can be
    found at the row matching that key with the biggest id. This makes it easy
    to roll back the database in case of people like Ankita defacing it.
    """

    # A short, stable way to identify the label and description.
    key = models.CharField(max_length=65535)

    # A one-line, human-readable label.
    label = models.CharField(max_length=65535)

    # A multi-line, human-readable description.
    descr = models.TextField()
