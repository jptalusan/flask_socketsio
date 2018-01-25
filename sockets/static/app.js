$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', function() {
        socket.emit('client_connected', {data: 'new client!'});
    });

    socket.on('alert', function(data) {
        alert('Alert Message!!: ' + data);
        //$('body').html('<p>HELLO!</p>');
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
        var data =  "{\"topic\":\"hello/world\"}";
        socket.emit('mqtt subscribe', data);
        console.log('on subscribe button click ' + data);
    });
    
    $("#unsubscribe").click(function() {
        var data =  "{\"topic\":\"hello/world\"}";
        socket.emit('mqtt unsubscribe', data);
        console.log('on unsubscribe button click ' + data);
    });

    $("#startMaster").click(function() {
        var data = "{\"topic\":\"master/start/flask\", \"payload\":\"start training\"}";
        socket.emit('mqtt startMaster', data);
        console.log('starting query...');
    });

    $("#query").click(function() {
        var data = "{\"topic\":\"flask/+/#\"}";
        socket.emit('mqtt_query_nodes', data);
        console.log('starting query...');
    });

    socket.on('mqtt_query_response', function(data) {
        //var payload = data.payload;
        if ($('#status').length > 0) {
            var div = document.getElementById('status');
            div.parentNode.removeChild(div);
        }
        console.log(data.length);
        for (i = 0; i < data.length; ++i) { 
            var obj = JSON.parse(data[i]);
            console.log('receiving message via mqtt ' + obj.ipaddress);
            var div;
            if ($('#status').length <= 0) {
                div = document.createElement('div');
                div.id = 'status';
                document.body.appendChild(div);
            } else {
                div = document.getElementById('status');
            }
            //div.innerHTML += obj.ipaddress;
            var nodeDiv = document.createElement('div');
            nodeDiv.id = 'node' + i;
            nodeDiv.innerHTML += '<h2>' + obj.node + '</h2>';
            
            var list = document.createElement('ul');
            list.id = 'node' + i + 'List';

            var ipaddress = document.createElement('li');
            ipaddress.innerHTML += obj.ipaddress;

            var status = document.createElement('li');
            status.innerHTML += obj.status;

            var availability = document.createElement('li');
            availability.innerHTML += obj.availability;

            div.appendChild(nodeDiv);
            nodeDiv.appendChild(list);
            list.appendChild(ipaddress);
            list.appendChild(status);
            list.appendChild(availability);

        }
    });
});
