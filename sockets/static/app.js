$(document).ready(function() {
    client = new Paho.MQTT.Client(location.hostname, Number(1884), "clientId");
    // set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // connect the client
    client.connect({onSuccess:onConnect});


    // called when the client connects
    function onConnect() {
      // Once a connection has been made, make a subscription and send a message.
      console.log("onConnect");
      client.subscribe("flask/+/#");
      // message = new Paho.MQTT.Message("Hello");
      // message.destinationName = "World";
      // client.send(message);
    }

    // called when the client loses its connection
    function onConnectionLost(responseObject) {
      if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:"+responseObject.errorMessage);
      }
    }

    // called when a message arrives
    function onMessageArrived(message) {
      console.log("onMessageArrived:"+message.payloadString);
      console.log("onMessageArrived:"+message.topic);
      topic = "flask/master/config";
      if (topic.localeCompare(message.topic) == 0) {
        console.log("flask/master/config:"+message.payloadString);
        var p = document.getElementById('masterConfig');
        p.innerHTML = message.payloadString;
      }
    }

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

    $("#getMasterConfig").click(function() {
      message = new Paho.MQTT.Message("get configs");
      message.destinationName = "master/config/get";
      client.send(message);
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

    $("#deleteDB").click(function() {
        socket.emit('deleteDB', "hello");
        console.log('on deleteDB');
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

        left = document.getElementById('left');
        
        var parse_json = JSON.parse(data)
        console.log(parse_json.length);
        console.log(parse_json)

        for (i = 0; i < parse_json.length; ++i) {
            console.log(parse_json[i].nodename)
            console.log(parse_json[i].datafile)
            console.log(parse_json[i].status)
            console.log(parse_json[i].ipaddress)
            console.log(parse_json[i].masternode_name)
            var div;
            if ($('#status').length <= 0) {
                div = document.createElement('div');
                div.id = 'status';
                left.appendChild(div);
            } else {
                div = document.getElementById('status');
            }
            //div.innerHTML += obj.ipaddress;
            var nodeDiv = document.createElement('div');
            nodeDiv.id = 'node' + i;
            nodeDiv.innerHTML += '<h2>' + parse_json[i].nodename + '</h2>';
            
            var list = document.createElement('ul');
            list.id = 'node' + i + 'List';

            var ipaddress = document.createElement('li');
            ipaddress.innerHTML += parse_json[i].ipaddress;

            var status = document.createElement('li');
            status.innerHTML += parse_json[i].status;

            var datafile = document.createElement('li');
            datafile.innerHTML += parse_json[i].datafile;

            var masternode = document.createElement('li');
            masternode.innerHTML += parse_json[i].masternode_name;

            div.appendChild(nodeDiv);
            nodeDiv.appendChild(list);
            list.appendChild(ipaddress);
            list.appendChild(status);
            list.appendChild(datafile);
            list.appendChild(masternode);
        }
    });
});
