ymaps.ready(init);
let resp_data;
let geoshow_data;
let general_map;
let elements = []

function init() {
    let myMap = new ymaps.Map("map", {
        center: [55.72, 37.64],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']

    }, {
        searchControlProvider: 'yandex#search'
    });
    general_map = myMap

}


function showHistoryData() {
    console.log(geoshow_data)

    var myGeoObject = new ymaps.GeoObject({
        // Описываем геометрию геообъекта.
        geometry: geoshow_data,
        // fillRule: "nonZero"
        properties: {
            balloonContent: "Многоугольник"
        }
    }, {
        fillColor: '#00FF00',
        strokeColor: '#0000FF',
        opacity: 0.5,
        strokeWidth: 3,
        strokeStyle: 'solid'
    });
    general_map.geoObjects.add(myGeoObject);
    general_map.setBounds(general_map.geoObjects.getBounds());
}


$("form[name='uploader']").submit(function (e) {
    let formData = new FormData($(this)[0]);
    alert("Если в файле tfw допущена ошибка, то отмеченные тропинки будут смещены. Обработка может занять некоторое время");
    elements.map(el => {el.remove()})
    $.ajax({
        url: '/api/upload_file',
        type: "POST",
        data: formData,
        async: false,
        success: function (msg) {
            resp_data = msg;
            show_result();
        },
        error: function (msg) {
            console.log(msg)
            alert('Ошибка!');
        },
        cache: false,
        contentType: false,
        processData: false
    });
    e.preventDefault();
});

function getFile(fileName) {
    let request = new XMLHttpRequest();
    request.open('GET', fileName);
    request.onloadend = function () {
        parse(request.responseText);
    }
    request.send();
}

function parse(obj) {
    geoshow_data = JSON.parse(obj);
    showHistoryData();
}



function show_result() {
    getFile(`/uploads/${resp_data.name_geoshow}`);

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

    var geo_download = document.createElement('a');
    geo_download.appendChild(document.createTextNode("Скачать geojson"));
    geo_download.href = `/uploads/${resp_data.name_geodata}`;
    geo_download.download = `/uploads/${resp_data.name_geodata}`;
    geo_download.className = "btn btn-secondary btn-block my-3";
    document.getElementById('geodata_json').appendChild(geo_download);

    elements = [newImg, newImg2, newImg3, geo_download]
}