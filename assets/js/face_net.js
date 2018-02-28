import client from 'socket.io-client';

const preloader = $('<img class="preloader" src="/static/img/preloader.gif" width="35">');

$('.face-net .update').click(function() {
    const type = $(this).data('type');
    const socket = client.connect('http://' + document.domain + ':' + location.port);
    // const socket = io('http://' + document.domain + ':' + location.port);
    let $this = $(this).parent();
    let $logs = $('<div class="logs well"></div>');
    socket.on('connect', function() {
        socket.emit('update', {name: type});
        $this.append(preloader);
        $this.append($logs);

        socket.on('logggged', function(data) {
            console.log('event 123', data);
            $this.find('.logs').append(data);
        });
    });
    socket.on('log', function(data) {
        console.log('event', data);
        $this.find('.logs').append(data);
    });
    socket.on('disconnect', function(){});
});