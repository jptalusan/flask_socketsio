$(document).ready(function() {
 var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
 socket.emit('client_connected', {data: 'new client!'});
 });

socket.on('alert', function(data) {
 alert('Alert Message!!: ' + data);
 });

socket.on('message', function(data) {
 console.log('message from backend ' + data);
 var time = new Date($.now());
 $('#test').html('<p>' + time + '</p>');
 });

$("#jsonbutton").click(function() {
 socket.send('{"message": "test"}');
 });

$("#alertbutton").click(function() {
 socket.emit('alert_button', 'Message from client!!');
 console.log('Pressed button alert');
 });
});
