FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-devel

RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc \
    libpq-dev \
    gcc 

RUN pip install albumentations==0.5.2
RUN pip install Flask==2.0.2
RUN pip install numpy==1.20.3
RUN pip install opencv_python_headless==4.5.1.48
RUN pip install segmentation_models_pytorch==0.2.0
RUN pip install pyproj==3.2.1
RUN pip install geojson==2.5.0

COPY static ./static/
COPY templates ./templates/
COPY uploads ./uploads/
COPY app.py .
COPY RoadDetection.py .
COPY best_model_LinkNet34.pth .

CMD python app.py