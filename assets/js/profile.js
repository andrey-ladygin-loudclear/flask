import Vue from 'vue';

let Webcam = require('./webcam.min');

// let profile_images = Vue.extend({
//     template: `<div v-on:profileImage="handleProfileImage"><h2>Profile images</h2>
//             <div v-for="path in images">
//                 <img :src="path" class="img-thumbnail"  width="100" />
//             </div>
//             <div class="loader" v-if="loading">
//                 <img class='preloader' src='/static/img/preloader.gif' width='80'/>
//             </div>
//         </div>`,
//     props: {
//         loading: false,
//         text: false,
//         images: []
//     },
//     methods: {
//         handleProfileImage: function(path) {
//             this.images.push(path)
//         },
//         isLoading: function(is_load) {
//             this.loading = !!is_load;
//         }
//     }
// });
//
// Vue.component('profile-images', profile_images);

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
            Webcam.snap(this.upload_image);
        },
        upload_image: function (data_uri) {
            let _this = this;

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
                    _this.image_processing = false;

                    if (response.success) {
                        _this.message = $('<div class="alert alert-success">Photo Added!</div>');
                        _this.$emit('profileImage', { path: response.path });
                        //$('.profile-images').append(`<img src="${response.path}" class="img-thumbnail"  width="100" />`)
                    } else {
                        _this.message = $(`<div class="alert alert-danger">${response.message}</div>`);
                        //_this.message = $('<div class="alert alert-danger">Please, put your face straight at the webcam!</div>');
                    }
                },
                error: function(jqXHR, textStatus, errorMessage) {
                    _this.image_processing = false;
                    console.error(errorMessage);
                }
            });
        }
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
