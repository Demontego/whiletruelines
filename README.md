# Отрисока троп на спутниковых снимках


### Установка

Необходимо установить используемые библиотеки
```
pip install -r requirements.txt
```
для установки необходимой версии pytorch перейдите на сайт https://pytorch.org/get-started/locally/

### Запуск и использование

Для запуска приложения, необходимо скачать репозиторий на ПК, выполнить установку вирутальной среды и командой ```python app.py``` запустить веб-сервер
После этого, по адресу `127.0.0.1:5000` будет доступен веб-интерфейс

Для работы с ним, необходимо загрузить изображение в поле загрузки и нажать на кнопку отправки. После обработки, через некоторе время, на сайте отобразится резльтат работы модели в виде размеченного изображения, маски и heatmap