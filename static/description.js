// Copyright (c) 2011 Stanford University
//
// Permission to use, copy, modify, and distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.
//
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR(S) DISCLAIM ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL AUTHORS BE LIABLE FOR ANY
// SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
// OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
// CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

// Depends on:
// - jQuery
// - fancybox
// - staticResources
// - publisher

// Edit the label and description for something.
// Pops up a dialog box with a form to edit the label and description of
// subject.
// The argument subject should have the fields:
//  - key: the key which identifies the label and description
//  - label: a single-line string
//  - description: a multi-line string
//  - labelDescChanges: a publisher (see static/publisher.js) that is to
//                      be called when the label and description have been changed.
DUMPSTR.editDescriptionAction = (function() {
    var description_form = DUMPSTR.staticResources.get(
                                'description_form.html');
    return function (subject) {
        description_form.whenReady(function (html) {
            var form = $(html);
            var label_input = $(':input[name=label]', form);
            var description_input = $(':input[name=description]', form);
            label_input.val(subject.label);
            description_input.val(subject.description);
            $.fancybox({content: form,
                        transitionIn: 'none',
                        transitionOut: 'none',
                        overlayShow: false, // slow
                        centerOnScroll: true});
            form.unbind('submit');
            form.bind('submit', function() {
                subject.label = label_input.val();
                subject.description = description_input.val();
                subject.labelDescChanges.publish();
                $.fancybox.showActivity();
                $.ajax({
                    type: 'POST',
                    cache: false,
                    url: DUMPSTR.WWW_ROOT + 'ajax/description/save/',
                    data: {
                        key: subject.key,
                        label: subject.label,
                        description: subject.description,
                    },
                    success: function(data) { $.fancybox.close(); },
                });
                return false;
            });
        });
    };
})();
