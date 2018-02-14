$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', function() {
        socket.emit('client_connected', {data: 'new client!'});
    });

    socket.on('detected_image', function(data) {
        src = "http://163.221.68.224:5001/uploads/person.jpg?" + new Date().getTime();
        // console.log('Received: ' + btoa(data));
        // console.log('Received: ' + Base64.decode(data));
        if ($('#img').length <= 0) {
            var img = document.createElement('img');
            img.id = "img";
            img.src = src;
            // img.src = 'data:image/jpeg;base64,' + btoa(data);
            // img.src = 'data:image/jpeg;base64,' + data;

            document.body.appendChild(img);
        } else {
            img = document.getElementById('img');
            img.src = src;
            // img.src = 'data:image/jpeg;base64,' + btoa(data);
        }
    });
});