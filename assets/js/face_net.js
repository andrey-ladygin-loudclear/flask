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

const bs = ['landmark', 'lfw', 'output', 'model'];

for (let i in bs) {
    socket.on(`log-${bs[i]}`, function(data) {
        $(`.bs-${bs[i]}`).find('.logs').prepend(data.message + "<br/>");
    });
    socket.on(`finish-${bs[i]}`, function(data) {
        let $node = $(`.bs-${bs[i]}`);
        $node.find('.info').html('');

        if (data.error) {
            //$node.find('.info').append('`<p><b>Error:</b> ${data.error}</p>`');
            $node.find('.logs').append(`<b>Error</b>: ${data.error}`)
        } else {
            finishUpdate($node);
            $node.find('.logs').append("Done! <br/>");
        }

        if (data.size) {
            $node.find('.info').append('`<p><b>Size:</b> ${data.size}</p>`');
        }
        if (data.message) {
            $node.find('.info').append('`<p class="alert alert-info"><b>Info:</b> ${data.message}</p>`');
        }
    });
}

let finishUpdate = function($node) {
    $node.removeClass('bs-callout-danger')
        .addClass('bs-callout-success')
        .find('.preloader')
        .remove();
};

socket.on('disconnect', function() {
    console.info('Socket disconnected');
});