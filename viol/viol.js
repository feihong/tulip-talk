(function() {
//=============================================================================
var messageHandlers = {};

var socket = new WebSocket('ws://' + window.location.host + '/socket');

socket.onmessage = function(evt) {
    var message = JSON.parse(evt.data);
    var selector = message.selector;
    var content = message.content;

    if (message.route in messageHandlers) {
        messageHandlers[message.route](content);
        return;
    }
    var groups = message.route.match(/jquery[.](\w+)/);
    if (groups) {
        var funcname = groups[1];
        var jq = jQuery(content.selector);
        var fn = jq[funcname];
        fn.apply(jq, content.args);
        return;
    }
    switch (message.route) {
        case 'log':
            console.log(content.value);
            break;
        default:
            console.log('Unable to handle message: ' + message)
    }
};

var register = function(route) {
    var parts = route.split(' ');
    var selector = parts.slice(0, parts.length - 1).join(' ');
    var eventName = parts[parts.length - 1];

    $(selector).on(eventName, function(evt) {
        if (eventName === 'submit') {
            evt.preventDefault();
        }
        var content = {}
        if (evt.target.tagName.toLowerCase() === 'form' && eventName === 'submit') {
            content = getFormValues(evt.target);
        }
        send(route, content);
    });
};

var send = function(route, content) {
    var mesg = JSON.stringify({
        route: route,
        content: content
    });
    socket.send(mesg);
};

var on = function(route, fn) {
    messageHandlers[route] = fn;
};

var getFormValues = function(form) {
    var result = {};
    $(form).find('input, select, textarea').each(function() {
        if (this.name) {
            result[this.name] = $(this).val();
        }
    });
    return result;
};

$(document).ready(function() {
    socket.onopen = function() {
        send('document_ready', null);
    };
});

$(window).on('unload', function() {
    send('window_unload', null);
});

window.viol = {
    register: register,
    send: send,
    on: on
};

//=============================================================================
})();
