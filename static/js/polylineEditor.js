ymaps.ready(init);
let data = [];
let userlines = [];

// TODO форма загрузки картинки
// TODO кнопка отправки картинки
//


function init() {
    let myMap = new ymaps.Map("map", {
        center: [55.72, 37.64],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']

    }, {
        searchControlProvider: 'yandex#search'
    });

    // Создаем ломаную.
    loadData(myMap)


    $('#startEditPolyline').click(
        function () {

            // $('#stopEditPolyline').attr('disabled', false);
            if (typeof polyline !== 'undefined') {
                data.push(polyline);
                polyline.editor.stopEditing();
            }

            polyline = new ymaps.Polyline([], {}, {
                strokeColor: '#00000088',
                strokeWidth: 4
            });

            myMap.geoObjects.add(polyline);
            polyline.editor.startEditing();
            polyline.editor.startDrawing();
            // $('#addPolyline').attr('disabled', true);
        });

    $('#stopEditPolyline').click(
        function () {
            polyline.editor.stopEditing();
            data.push(polyline);
        });

    $('#saveData').click(
        function () {
            sendData(data)
        }
    );


// Обработка нажатия на кнопку Удалить
    $('#dellPolyline').click(
        function () {
            data.pop()
            myMap.geoObjects.remove(polyline);
            $('#geometry').html('');
            // $('#addPolyline').attr('disabled', false);
        });


}

function showHistoryData(objects, map_obj) {
    console.log(objects.data)

    objects.map(function (el) {
        let tmp_line = new ymaps.Polyline(
            el.coord
            , {}, {
                strokeColor: "#00000088",
                strokeWidth: 4,
                editorMaxPoints: 50,
            });
        map_obj.geoObjects.add(tmp_line);
    });
}

function loadData(mmap) {
    return $.ajax({
        url: "http://127.0.0.1:5000/api/data",
        success: function (response) {
            console.log("Data Loaded: " + response);
        },
        dataType: "json"
    }).then(function (result) {
        console.log('result', result);
        return showHistoryData(result, mmap);
    });
}


// TODO исправить генерацию имени для линии
function generateName() {
    let today = new Date();
    let date = today.getFullYear() + '' + (today.getMonth() + 1) + '' + today.getDate();
    let time = today.getHours() + '' + today.getMinutes() + '' + today.getSeconds() + '' + today.getMilliseconds();
    let dateTime = date + '_' + time;
    return dateTime;
}

function prepareData(data) {
    return data.map(function (el) {
        return {'name': generateName(), 'coord': el.geometry.getCoordinates()};
    });
}

function sendData(dataList) {
    $.ajax({
        type: 'POST',
        url: 'http://127.0.0.1:5000/api/data',
        data: JSON.stringify(prepareData(dataList)),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (resp) {
            alert("Success");
            console.log("Data Loaded: " + resp.code);
        }
    });
}
