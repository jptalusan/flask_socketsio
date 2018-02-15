$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var timer;
    var fps_count = 0.0;
    var first_frame = false;
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

    socket.on('processed_image_by_slave', function(data) {
        if (!first_frame) {
            first_frame = true;
            timer = new Date();
        }
        fps_count++;
        var currentdate = new Date();
        var datetime = "Last Sync: " + currentdate.getDate() + "/"
                + (currentdate.getMonth()+1)  + "/" 
                + currentdate.getFullYear() + " @ "  
                + currentdate.getHours() + ":"  
                + currentdate.getMinutes() + ":" 
                + currentdate.getSeconds() + "."
                + currentdate.getMilliseconds();

        console.log('Received processed_image_from_slave: ' + datetime)
        if ($('#img').length <= 0) {
            var img = document.createElement('img');
            img.id = "img";
            img.src = 'data:image/jpeg;base64,' + data;

            document.body.appendChild(img);
        } else {
            img = document.getElementById('img');
            // img.src = src;
            // img.src = 'data:image/jpeg;base64,' + btoa(data);
            img.src = 'data:image/jpeg;base64,' + data;
        }
    });

    socket.on('fps_data', function(data) {
        var parse_json = JSON.parse(data)
        document.getElementById("elapsed").textContent = "Time elapsed: " + parse_json.elapsed;
        document.getElementById("fps").textContent = "FPS: " + parse_json.fps;
        // console.log(parse_json);
    });

    $("#start_bench").click(function() {
        console.log('starting bench...');
        socket.emit('bench_switch', 0);
        window.location.reload();
    });

    $("#stop_bench").click(function() {
        console.log('stopping bench...');
        socket.emit('bench_switch', 1);
        console.log('TOTAL FRAMES: ' + fps_count);
        curr_time = new Date();
        elapsed_time = curr_time - timer;
        console.log('ELAPSED_TIME IN SEC:' + (elapsed_time / 1000));
        secs = (elapsed_time / 1000).toFixed(2);
        fps = (fps_count/secs).toFixed(2);
        console.log('FPS: ' + fps)
        fps_count = 0;
    });

    // client = new Paho.MQTT.Client(location.hostname, Number(1884), "clientId2");
    // // set callback handlers
    // client.onConnectionLost = onConnectionLost;
    // client.onMessageArrived = onMessageArrived;

    // // connect the client
    // client.connect({onSuccess:onConnect});


    // // called when the client connects
    // function onConnect() {
    //   // Once a connection has been made, make a subscription and send a message.
    //   console.log("onConnect");
    //   client.subscribe("hello/server");
    // }

    // // called when the client loses its connection
    // function onConnectionLost(responseObject) {
    //   if (responseObject.errorCode !== 0) {
    //     console.log("onConnectionLost:"+responseObject.errorMessage);
    //   }
    // }

    // function decodeWebSocket (data){
    //     var datalength = data[1] & 127;
    //     var indexFirstMask = 2;
    //     if (datalength == 126) {
    //         indexFirstMask = 4;
    //     } else if (datalength == 127) {
    //         indexFirstMask = 10;
    //     }
    //     var masks = data.slice(indexFirstMask,indexFirstMask + 4);
    //     var i = indexFirstMask + 4;
    //     var index = 0;
    //     var output = "";
    //     while (i < data.length) {
    //         output += String.fromCharCode(data[i++] ^ masks[index++ % 4]);
    //     }
    //     return output;
    // }

    // // called when a message arrives
    // function onMessageArrived(message) {
    //   var currentdate = new Date(); 
    //     var datetime = "Last Sync: " + currentdate.getDate() + "/"
    //             + (currentdate.getMonth()+1)  + "/" 
    //             + currentdate.getFullYear() + " @ "  
    //             + currentdate.getHours() + ":"  
    //             + currentdate.getMinutes() + ":" 
    //             + currentdate.getSeconds();

    //     console.log('Received processed_image_from_slave: ' + console.log(datetime))
    //     if ($('#img').length <= 0) {
    //         var img = document.createElement('img');
    //         img.id = "img";
    //         img.src = 'data:image/jpeg;base64,' + decodeWebSocket(message);

    //         document.body.appendChild(img);
    //     } else {
    //         img = document.getElementById('img');
    //         // img.src = src;
    //         // img.src = 'data:image/jpeg;base64,' + btoa(data);
    //         img.src = 'data:image/jpeg;base64,' + decodeWebSocket(message);
    //     }
    // }
});