import Vue from 'vue';

let Webcam = require('./webcam.min');
//let Vue = require('vue');

Vue.component('mycounter', {
    //template: `<h1>Hi </h1>`
    template: '#counter-template',
    props: ['subject'],
    data: function() {
        return { count: 0 }
    }
});

let profile_images = Vue.extend({
    template: `<div><h2>Profile images</h2><div class="loader" v-if="loading">
       <img class='preloader' src='/static/img/preloader.gif' width='80'/></div>{{ text }}</div>`,
    props: {
        loading: false,
        text: false
    },
    watch: {
        isLoading: function(is_load) {
            this.loading = !!is_load;
        }
    }
});

Vue.component('profile-images', profile_images);

new Vue({
    el: '#webcam',
    template: `<div class="form-group">
                <label for="profile_image">Add Profile Image</label>
                <input type="file" id="profile_image">
                <div id="my_camera"></div>
                <input type=button value="Take Snapshot" v-on:click="take_snapshot">
                <p class="help-block">Add your images for face auth</p>
                <profile-images v-bind:loading="image_processing"></profile-images>
            </div>`,
    data: {
        points: 500,
        count: 0,
        image_processing: false,
        message: ''
    },
    created: function() {
        navigator.mediaDevices.getUserMedia({
            video: true
        }).then(this.webcam_init);
    },
    methods: {
        webcam_init: function() {
            Webcam.set({
                width: 320,
                height: 240,
                image_format: 'jpeg',
                jpeg_quality: 90
            });
            Webcam.attach('#my_camera');
        },
        take_snapshot: function (e) {
            this.image_processing = true;

            setTimeout(this.upload_image, 1000);
            // Webcam.snap( function(data_uri) {
            //     $('.profile-images').append("<img class='preloader' src='/static/img/preloader.gif' width='80'/>");
            //     $('.alert').remove();
            //     uploadFile(data_uri);
            // } );
        },
        upload_image: function () {
            this.image_processing = false;
        }
    },
    components: {
        profile_images
    }
});

Vue.component('my-webcam', {
    template: `<div class="form-group">
                <label for="profile_image">Add Profile Image</label>
                <input type="file" id="profile_image">
                <div id="my_camera"></div>
                <input type="button" value="Take Snapshot" v-on:click="take_snapshot">
                <p class="help-block">Add your images for face auth</p>
            </div>`,
    props: [],
    created: function() {
        Webcam.set({
            width: 320,
            height: 240,
            image_format: 'jpeg',
            jpeg_quality: 90
        });
        Webcam.attach( this.template );
    },
    data: function() {
        return {}
    }
});

if ($('.profile_____').length) {
    Webcam.set({
        width: 320,
        height: 240,
        image_format: 'jpeg',
        jpeg_quality: 90
    });
    Webcam.attach( '#my_camera' );

    $('#take_snapshot').click(take_snapshot);

    function take_snapshot () {
        Webcam.snap( function(data_uri) {
            $('.profile-images').append("<img class='preloader' src='/static/img/preloader.gif' width='80'/>");
            $('.alert').remove();
            uploadFile(data_uri);
        } );
    };

    function uploadFile (data_uri) {
        let formData = new FormData();
        formData.append("fileToUpload", data_uri);

        $.ajax({
            url: "/upload_profile_image",
            type: "POST",
            dataType: 'json',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                let $alert;

                if (response.success) {
                    $alert = $('<div class="alert alert-success">Photo Added!</div>');
                    $('.profile-images').append(`<img src="${response.path}" class="img-thumbnail"  width="100" />`)
                } else {
                    $alert = $('<div class="alert alert-danger">Please, put your face straight at the webcam!</div>');
                }

                $('.preloader').remove();
                $('#my_camera').after($alert);
            },
            error: function(jqXHR, textStatus, errorMessage) {
                $('.preloader').remove();
                console.error(errorMessage); // Optional
            }
        });
    }
}