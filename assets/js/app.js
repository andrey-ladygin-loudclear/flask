require('./bootstrap');
require('./face_net');
let Webcam = require('./webcam.min');


//<!-- Configure a few settings and attach camera -->
if ($('.profile').length) {
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