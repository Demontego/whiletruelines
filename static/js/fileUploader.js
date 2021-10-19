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
            console.log(resp_data);
            subscribe();
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

function show_result() {
    console.log('DONE')
    if (resp_data.status === 'done') {
        console.log('resp_data.status === done')
        $('img').attr('src', `/get_file/${resp_data.name}`);
    }

}

function check_status() {
    return $.ajax({
        url: `/api/get_status_file/${resp_data.name}`,
        success: function (response) {
        },
        dataType: "json"
    }).then(function (result) {
        console.log('check_status', result.status);
        resp_data = result;
    });
}


async function subscribe() {
    // let response = await fetch(`/api/get_status_file/${resp_data.name}`);
    let response = await check_status();
    if (response.status == 502) {
        await subscribe();
    } else if (response.status != 200) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        await subscribe();
    } else {
        // Получим и покажем сообщение
        let msg = await response;
        console.log(msg);
        if (msg.status === 'done') {
            console.log('is Done')
            resp_data = msg;
            show_result();
            console.log("kek")
        } else {
            await new Promise(resolve => setTimeout(resolve, 1000));
            await subscribe();
        }
    }
}

