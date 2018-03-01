import client from 'socket.io-client';

const preloader = '<img class="preloader" src="/static/img/preloader.gif" width="35">';

const socket = client.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.info('Socket connected');
});

$('.face-net .update').click(function() {
    const type = $(this).data('type');
    let $this = $(this).parent();
    let $logs = $('<div class="logs well"></div>');

    socket.emit('update', {name: type});
    $this.append($(preloader));
    $this.append($logs);
});

socket.on('log-landmark', function(data) {
    $('.bs-landmark').find('.logs').append(data.message);
});
socket.on('log-lfw', function(data) {
    $('.bs-lfw').find('.logs').append(data.message);
});
socket.on('log-callout', function(data) {
    $('.bs-callout').find('.logs').append(data.message);
});

socket.on('disconnect', function() {
    console.info('Socket disconnected');
});