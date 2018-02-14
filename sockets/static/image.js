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
    });
});