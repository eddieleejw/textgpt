FROM python:3.12

WORKDIR /textgpt-app

COPY requirements_docker.txt .

RUN pip install -r requirements_docker.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY ./utils ./utils

COPY main.py main.py

CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]