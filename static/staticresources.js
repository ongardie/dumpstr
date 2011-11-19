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
// - publisher

// An object with the following methods:
//  - get: Takes a resource name and returns a resource object.
//
// A resource object has the following methods:
//  - whenReady: The only argument is a function that takes a string with the
//               contents of the static resource file. This function is called
//               exactly once, either immediately if the resource has already
//               been fetched, or once the resource has been retrieved.
DUMPSTR.staticResources = (function() {
    var cache = {};

    var makeResource = function (resource_name) {
        var loading = false; // whether the AJAX request has been fired off
        var isReady = false; // whether the resource has been successfully retrieved
        var resource = ''; // a placeholder for the contents of the resource
        var onReady = DUMPSTR.createPublisher(); // notifies when isReady becomes true
        // fire off the AJAX request
        var load = function () {
            loading = true;
            $.ajax({
                url: DUMPSTR.STATIC_URL + resource_name,
                success: function (data) {
                    isReady = true;
                    resource = data;
                    onReady.publish();
                },
            });
        };
        return {
            whenReady: function (action) {
                if (isReady) {
                    action(resource);
                } else {
                    onReady.subscribe(function () { action(resource); });
                    if (!loading)
                        load();
                }
            }
        }
    };

    return {
        get: function (resource_name) {
            if (resource_name in cache) {
                return cache[resource_name];
            } else {
                var resource = makeResource(resource_name);
                cache[resource_name] = resource;
                return resource;
            }
        },
    };
})();
