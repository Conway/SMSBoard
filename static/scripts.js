$(document).ready(function() {
    var url = "http://" + document.domain + ":" + location.port;
    var socket = io.connect(url + "/soc");
    socket.on('count', function(count) {
        $("#viewing").html(count.count + " people viewing");
    });
    socket.on('message', function(message) {
        $("#messages").prepend('<li class="list-group-item"><h4 class="list-group-item-heading">' + message.message + '</h4><p class="list-group-item-text">' + message.sender + '</p></li>');
        notifyMe(message.message);
    });
});

//source: http://stackoverflow.com/a/13328513/7090605

document.addEventListener('DOMContentLoaded', function() {
    if (!Notification) {
        alert('Desktop notifications not available in your browser.');
        return;
    }

    if (Notification.permission !== "granted")
        Notification.requestPermission();
});

function notifyMe(text) {
    if (Notification.permission !== "granted")
        Notification.requestPermission();
    else {
        var notification = new Notification('A new message was posted', {
            body: text,
            icon: "/static/exclaim.png",
        });
        notification.onclick = function(x) {
            window.focus();
            this.cancel();
        }
    }
}
