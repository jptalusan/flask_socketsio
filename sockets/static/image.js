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
        if ($('#img').length <= 0) {
            var img = document.createElement('img');
            img.id = "img";
            img.src = src;
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

        // console.log('Received processed_image_from_slave: ' + datetime)
        if ($('#img').length <= 0) {
            var img = document.createElement('detected_video');
            img.id = "img";
            img.src = 'data:image/jpeg;base64,' + data;

            document.body.appendChild(img);
        } else {
            img = document.getElementById('detected_video');
            img.src = 'data:image/jpeg;base64,' + data;
        }

        curr_time = new Date();
        elapsed_time = curr_time - timer;
        // console.log('ELAPSED_TIME IN SEC:' + (elapsed_time / 1000));
        secs = (elapsed_time / 1000).toFixed(2);
        fps = (fps_count/secs).toFixed(2);

        document.getElementById("det_elapsed").textContent = "Time elapsed: " + secs;
        document.getElementById("det_fps").textContent = "FPS: " + fps;
    });

    socket.on('fps_data', function(data) {
        var parse_json = JSON.parse(data)
        document.getElementById("elapsed").textContent = "Time elapsed: " + parse_json.elapsed;
        document.getElementById("fps").textContent = "FPS: " + parse_json.fps;
        // console.log(parse_json);
    });

    socket.on('number_of_nodes', function(value) {
        console.log('value: ' + value);
        $("input[name=opt][value=" + value + "]").prop("checked", true);
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
        first_frame = false;
    });

    $('input[name=opt]').change(function(){
        var value = $( 'input[name=opt]:checked' ).val();
        if (value == 0) {
            data = "";
            // console.log('Received processed_image_from_slave: ' + datetime)
            if ($('#img').length <= 0) {
                var img = document.createElement('detected_video');
                img.id = "img";
                img.src = 'data:image/jpeg;base64,' + data;

                document.body.appendChild(img);
            } else {
                img = document.getElementById('detected_video');
                img.src = 'data:image/jpeg;base64,' + data;
            }
        }
        Cookies.set('number_of_nodes2', value);
        console.log("Nodes: " + value);
        socket.emit('number_of_nodes2', {data: value});
        // Reset timers
        fps_count = 0;
        first_frame = false;
        timer = new Date();
    });
});