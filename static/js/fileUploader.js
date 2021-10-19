// TODO форма загрузки картинки
// TODO кнопка отправки картинки


let resp_data;

$("form[name='uploader']").submit(function (e) {
    console.log("catched")
    let formData = new FormData($(this)[0]);

    $.ajax({
        url: '/upload_file',
        type: "POST",
        data: formData,
        async: false,
        success: function (msg) {
            alert(msg);
            resp_data = msg;
            $('#fileData').html(msg);
            console.log(resp_data)
        },
        error: function (msg) {
            alert('Ошибка!');
        },
        cache: false,
        contentType: false,
        processData: false
    });
    e.preventDefault();
});

