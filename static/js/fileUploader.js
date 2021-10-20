let resp_data;
// let resp_data = {
//     "name": "eC7F2662dd75Cf82a65F4b7713CA8D9Fa",
//     "ext": "png",
//     "driveIn_id": "1LhRV2tP4jAfY9RcE0UHpHKc-eAw9_UJT",
//     "driveOut_id": "",
//     "status": "wait",
//     "coord": [],
//     "tag": "img"
// }

$("form[name='uploader']").submit(function (e) {
    console.log("catched")
    let formData = new FormData($(this)[0]);

    $.ajax({
        url: '/upload_file',
        type: "POST",
        data: formData,
        async: false,
        success: function (msg) {
            alert("Success");
            resp_data = msg;
            $('#fileData').html(msg);
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
    var newImg = document.createElement('img');
    newImg.src = `https://drive.google.com/uc?export=view&id=${resp_data.driveIn_id}`;
    newImg.alt = 'alt text';
    newImg.class = "img-fluid";
    document.getElementById('respPict').appendChild(newImg);
}


function check_status() {
    return $.ajax({
        url: `/api/get_status_file/${resp_data.name}`,
        success: function (response) {
            return response;
        },
        dataType: "json"
    }).then(function (result) {
        resp_data = result;
    });
}


async function subscribe() {
    check_status();
    if (resp_data.status === 'done') {
        show_result();
    } else {
        await new Promise(resolve => setTimeout(resolve, 3000));
        await subscribe();
    }
}
