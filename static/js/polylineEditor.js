ymaps.ready(init);
let data = [];
let userlines = [];


function init() {
    var myMap = new ymaps.Map("map", {
        center: [55.72, 37.64],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']

    }, {
        searchControlProvider: 'yandex#search'
    });

    // Создаем ломаную.

    /*
    var current_polyline1 = new ymaps.Polyline([
        // Указываем координаты вершин.
        [55.80, 37.50],
        [55.80, 37.40],
        [55.70, 37.50],
        [55.70, 37.40]
    ], {}, {
        strokeColor: "#00000088",
        strokeWidth: 4,
        editorMaxPoints: 50,

        // Добавляем в контекстное меню новый пункт, позволяющий удалить ломаную.
        editorMenuManager: function (items) {
            items.push({
                title: "Удалить линию",
                onClick: function () {
                    myMap.geoObjects.remove(current_polyline);
                }
            });
            return items;
        }
    });
*/

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

            // printGeometry(polyline.geometry.getCoordinates());


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

// TODO исправить генерацию имени для линии
function generateName() {
    setTimeout(function (){}, 10)
    var today = new Date();
    var date = today.getFullYear() + '' + (today.getMonth() + 1) + '' + today.getDate();
    var time = today.getHours() + '' + today.getMinutes() + '' + today.getSeconds() + '' + today.getMilliseconds();
    var dateTime = date + '_' + time;
    return dateTime;
}

function prepareData(data) {
    return data.map(function (el) {
        return {'name': generateName(), 'coord': el.geometry.getCoordinates()};
    });
}

function sendData(dataList) {
    printList(data);
    $.ajax({
        type: 'POST',
        url: 'http://127.0.0.1:5000/api/data',
        data: JSON.stringify(prepareData(dataList)),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (resp) {
            console.log("Data Loaded: " + resp.code);
        }
    });
}

function printList(objects) {

    $('#objlist').html(getList(objects));

    function getList(objects_list) {
        let result = "";

        if ($.isArray(objects_list)) {
            for (var i = 0, l = objects_list.length; i < l; i++) {
                if (i > 0) {
                    result += '<a href="#" class="list-group-item list-group-item-action active">' + objects_list[i].geometry.getCoordinates()[0] + '</a>';
                }
            }
        }
        return result;
    }
}