FROM python:3.12

WORKDIR /textgpt-app

COPY requirements_docker.txt .

RUN pip install -r requirements_docker.txt

COPY ./utils ./utils

COPY streamlit.py streamlit.py

CMD ["streamlit", "run", "streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]