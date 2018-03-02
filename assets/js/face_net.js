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
    $('.bs-landmark').find('.logs').prepend(data.message + "<br/>");
    console.log(data.message + "<br/>");
});
socket.on('log-lfw', function(data) {
    $('.bs-lfw').find('.logs').prepend(data.message + "<br/>");
});
socket.on('log-callout', function(data) {
    $('.bs-output').find('.logs').prepend(data.message + "<br/>");
});

socket.on('finish-landmark', function(data) {
    finishUpdate($('.bs-landmark'));
    $('.bs-landmark .info').html(`<p><b>Size:</b> ${data}</p>`);
});
socket.on('finish-lfw', function(data) {
    finishUpdate($('.bs-lfw'));
    $('.bs-lfw .info').html(`<p><b>Size:</b> ${data}</p>`);
});
socket.on('finish-callout', function(data) {
    finishUpdate($('.bs-output'));
    $('.bs-output .info').html(`<p><b>Size:</b> ${data}</p>`);
});

let finishUpdate = function($node) {
    $node.removeClass('bs-callout-danger')
        .addClass('bs-callout-success')
        .find('.logs, .preloader')
        .remove();
};

socket.on('disconnect', function() {
    console.info('Socket disconnected');
});