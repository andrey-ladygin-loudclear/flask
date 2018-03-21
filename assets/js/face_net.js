import client from 'socket.io-client';
import Vue from 'vue';

const preloader = '<img class="preloader" src="/static/img/preloader.gif" width="35">';

const socket = client.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.info('Socket connected');
});

$('.face-net .update').click(function() {
    const type = $(this).data('type');
    let $this = $(this).parent();
    let $logs = $('<div class="logs well"></div>');

    console.log('emit update', type);
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

// let template = `<div class="bs-callout bs-landmark {% if net.landmarks %}bs-callout-success{% else %}bs-callout-danger{% endif %}">
//             <h4>{{ name }}</h4>
//             <p>path: {{ net.landmarks_path }}</p>
//             <div class="info">
//                 {{ info }}
//                 {% if net.landmarks %}
//                     <p><b>Size</b>: {{ net.landmarks }}</p>
//                 {% else %}
//                     <p>No File</p>
//                 {% endif %}
//             </div>
//             <button class="btn btn-info update" data-type="landmarks">Download</button>
//         </div>`;
// let Vue = require('vue');
// Vue.component('callout', {
//     template: template,
//     //template: '#counter-template',
//     props: ['subject'],
//     data: function() {
//         return {
//             name: 'Weights',
//             info: `<p><b>Size</b>: ${size}</p>`,
//             count: 0
//         }
//     }
// });

// Vue.component('callout', new Vue({
//     //el: '#callout',
//     el: 'callout',
//     //template: '#callout-template',
//     delimiters: ['{(', ')}'],
//     data: {
//         loading: false,
//         status: false,
//         info: 'default',
//         message: 'adawdaw',
//     },
//     // created: function () {
//     //     console.info('mounted', this.info)
//     // },
//     methods: {
//         update: function() {
//             console.log('Update', this.info);
//             this.info += ' 1'
//         }
//     }
// }));


Vue.component('callout', {
    template: '<div><h4>{{title}}</h4><div class="info">{{info}}</div><button v-on:click="update" class="btn btn-info update">Update</button></div>',
    // template: '#callout-template',
    // delimiters: ['{(', ')}'],
    props: ['title'],
    data() {
        return {
            loading: false,
            info: 'default',
            counter: 1,
            message: 'test'
        }
    },
    methods: {
        update: function() {
            this.counter += 1;
            this.message = 'test ' + this.counter;
        }
    }
});

new Vue({
    el: '#callout-list',
});
