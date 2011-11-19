DUMPSTR.createPublisher = function() {
    var subscribers = [];
    return {
        subscribe: function(callback) {
            return subscribers.push(callback) - 1;
        },
        unsubscribe: function(id) {
            // This code intentionally does not re-index the remainder of the
            // array so that previously returned indexes are still valid.
            delete subscribers[id];
        },
        publish: function() {
            for (var idx in subscribers) {
                var callback = subscribers[idx];
                callback();
            }
        },
    };
};
