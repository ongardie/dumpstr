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

// Depends on jquery.flot.js, jquery.flot.selection.js, publisher.js.
// Depends on:
// - jQuery
// - flot
// - publisher
// - staticResources
// - description

// Add a new trend graph to the page.
// container: jQuery selector on which to append the trend graph on the page
// trendId: identifier for the trend
// label: a label to use for the graph
// description: a description for the graph
WEBMETRICS.addTrendGraph = function (container, trendId,
                                     key, label, description) {
    var resource = WEBMETRICS.staticResources.get('trendgraph.html');
    resource.whenReady(function (trendGraphTpl) {
        var cloned = $(trendGraphTpl);
        container.append(cloned);
        $("h3", cloned).html(label);
        $("span", cloned).html(description);
        WEBMETRICS.createTrend(trendId,
                            $(".graph-placeholder", cloned),
                            $(".zoom-out", cloned),
                            $(".pointinfo-placeholder", cloned));

        // Update the row label and descriptions when they change
        var descSubject = {
            key: key,
            label: label,
            description: description,
            labelDescChanges: WEBMETRICS.createPublisher(),
        };
        descSubject.labelDescChanges.subscribe(function () {
            $("h3", cloned).html(descSubject.label);
            $("span", cloned).html(descSubject.description);
        });
        // Also set them now
        descSubject.labelDescChanges.publish();
        // And set the handler for the description edit link
        $("a", cloned).click(function() {
            WEBMETRICS.editDescriptionAction(descSubject);
        });
    });
}


// Graph a trend line.
// This is used internally by WEBMETRICS.addTrendGraph, and you should usually
// call that instead.
//
// trendId: identifier for the trend
// placeholder: jQuery selector result of where to place the chart.
//              This needs to be visible and have a fixed size for flot
//              to work.
// back: jQuery selector result for a zoom out button.
// pointInfo: jQuery selector result for displaying information about
//            selected points.
WEBMETRICS.createTrend = function (trendId, placeholder, back, pointInfo) {

    var data = [];
    var zooms = [];

    var formatTimestamp = function (unixtime) {
        var pad = function (num, digits) {
            var s = "" + num;
            while (s.length < digits)
                s = "0" + s;
            return s;
        };
        var d = new Date(unixtime * 1000);
        return pad(d.getFullYear(), 4) + '-' +
               pad(d.getMonth() + 1, 2) + '-' +
               pad(d.getDate(), 2) + ' ' +
               pad(d.getHours(), 2) + ':' +
               pad(d.getMinutes(), 2) + ':' +
               pad(d.getSeconds(), 2);
    };

    var redraw = function () {
        var showPoints = (data.length < 50);
        var xticks = [];
        if (data.length > 0) {
            var first = data[0];
            var middle = data[Math.floor(data.length / 2)];
            var last = data[data.length - 1];
            xticks.push([first[0],  formatTimestamp(first[2])]);
            xticks.push([middle[0], formatTimestamp(middle[2])]);
            xticks.push([last[0],   formatTimestamp(last[2])]);
        }
        $.plot(placeholder,
               [
                { data: data,
                  lines: {show: true},
                  points: {show: showPoints},
                },
               ],
               {
                 xaxis: {ticks: xticks},
                 yaxis: {labelWidth: 100, min: 0},
                 selection: { mode: "x" },
                 grid: {clickable: showPoints},
               });
    };

    var refetch = function () {
        var requestData = {};
        if (zooms.length > 0) {
            var last = zooms[zooms.length - 1];
            requestData.from = last[0];
            requestData.to = last[1];
        }
        $.ajax({
            url: WEBMETRICS.WWW_ROOT + 'ajax/trend/' + trendId,
            type: 'GET',
            data: requestData,
            dataType: 'json',
            success: function (newData) {
                if (newData.length > 3 || zooms.length <= 1) {
                    data = newData;
                    redraw();
                } else {
                    console.log("Too few data points to be interesting");
                    zooms.pop();
                }
            },
        });
    };

    redraw();

    placeholder.bind("plotclick", function (event, pos, item) {
        if (item === null) {
            pointInfo.html("");
            return;
        }

        var details = data[item.dataIndex];
        var pointId = details[0];
        var value = details[1];
        var timestamp = details[2];
        var reportId = details[3];

        var html = [];
        html.push("Selected point:");
        html.push(formatTimestamp(timestamp));
        html.push("Value: " + value);
        if (details[3] > 0) {
            html.push("Report: <a href=\"" + WEBMETRICS.WWW_ROOT +
                      "report/" + reportId + "\">" +
                      reportId + "</a>");
        }
        pointInfo.html(html.join("<br />"));
    });

    placeholder.bind("plotselected", function (event, ranges) {
        var range = ranges.xaxis; // has .from and .to that are floats
        console.log("Zooming to [" + range.from + ", " + range.to + "]");
        zooms.push([range.from, range.to]);
        refetch();
    });

    back.click(function () {
        zooms.pop();
        refetch();
    });

    refetch();
};
