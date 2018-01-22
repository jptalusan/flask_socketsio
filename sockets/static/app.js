$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        socket.emit('client_connected', {data: 'new client!'});
    });

    socket.on('alert', function(data) {
        alert('Alert Message!!: ' + data);
    });

    socket.on('message', function(data) {
        console.log('js: on message');
        console.log('message from backend ' + data);
        var time = new Date($.now());
        console.log(time);
        $('#test').html('<p>' + time + '</p>');
    });
    
    socket.on('my event', function(data) {
        console.log('message from backend ' + data);
    });

    $("#jsonbutton").click(function() {
        socket.emit('my event', '{"message":"test"}');
        socket.send('{"message": "test"}');
    });

    $("#alertbutton").click(function() {
        socket.emit('alert_button', 'Message from client!!');
        console.log('Pressed button alert');
    });

    socket.on('mqtt_message', function(data) {
        console.log('receiving message via mqtt.');
        //var obj = jQuery.parseJSON(data);
        $('#mqtt').html('<p>' + data.payload + '</p>');
    });

    $("#subscribe").click(function() {
        var data =  "{\"topic\":\"hello/world\"}"
        socket.emit('mqtt subscribe', data);
        console.log('on subscribe button click ' + data);
    });
});
