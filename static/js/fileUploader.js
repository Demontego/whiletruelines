let resp_data;

$("form[name='uploader']").submit(function (e) {
    let formData = new FormData($(this)[0]);

    $.ajax({
        url: '/api/upload_file',
        type: "POST",
        data: formData,
        async: false,
        success: function (msg) {
            alert("Обработка может занять некоторое время");
            resp_data = msg;
            show_result();
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
    newImg.src = `/uploads/${resp_data.name_image}`;
    newImg.alt = 'done';
    newImg.class = "img-fluid top-cover center-block";
    newImg.style = "max-width: 100%; height: auto;"
    document.getElementById('fileData_done').appendChild(newImg);

    var newImg2 = document.createElement('img');
    newImg2.src = `/uploads/${resp_data.name_mask}`;
    newImg2.alt = 'mask';
    newImg2.class = "img-fluid";
    document.getElementById('fileData_mask').appendChild(newImg2);

    var newImg3 = document.createElement('img');
    newImg3.src = `/uploads/${resp_data.name_heatmap}`;
    newImg3.alt = 'heatmap';
    newImg3.class = "img-fluid";
    document.getElementById('fileData_heatmap').appendChild(newImg3);
}