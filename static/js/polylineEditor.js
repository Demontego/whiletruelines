ymaps.ready(init);
let data = [];
let userlines = [];


function init() {
    // Создаем карту.
    var myMap = new ymaps.Map("map", {
        center: [55.72, 37.64],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector',  'fullscreenControl']

    }, {
        searchControlProvider: 'yandex#search'
    });

    // Создаем ломаную.
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

    var current_polyline = new ymaps.Polyline([], {}, {
        strokeColor: '#00000088',
        strokeWidth: 4
    });


    // TODO вот это вынести на внешнюю кнопку
    // Добавляем линию на карту.
    myMap.geoObjects.add(current_polyline);

    // Включаем режим редактирования.
    current_polyline.editor.startEditing();
    current_polyline.editor.startDrawing();

    // $('input').attr('disabled', false);
    $('#startEditPolyline2').click(
        function () {
            // Отключаем кнопки, чтобы на карту нельзя было
            // добавить более одного редактируемого объекта (чтобы в них не запутаться).
            // $('input').attr('disabled', true);

            current_polyline.editor.stopEditing();

            // printGeometry(current_polyline.geometry.getCoordinates());

        });

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
            printGeometry(polyline.geometry.getCoordinates());
            // $('#stopEditPolyline').attr('disabled', true);

        });


    // Обработка нажатия на кнопку Удалить
    $('#dellPolyline').click(
        function () {

            myMap.geoObjects.remove(polyline);
            $('#geometry').html('');
            // $('#addPolyline').attr('disabled', false);
        });
}




function printGeometry(coords) {
    $('#geometry').html('Координаты: ' + stringify(coords));

    function stringify(coords) {
        var res = '';
        if ($.isArray(coords)) {
            res = '[ ';
            for (var i = 0, l = coords.length; i < l; i++) {
                if (i > 0) {
                    res += ', ';
                }
                res += stringify(coords[i]);
            }
            res += ' ]';
        } else if (typeof coords == 'number') {
            res = coords.toPrecision(6);
        } else if (coords.toString) {
            res = coords.toString();
        }

        return res;
    }
}