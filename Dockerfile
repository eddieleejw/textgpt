FROM python:3.12

ADD streamlit.py .

RUN pip install -r requirements_win.txt

CMD [ "streamlit", "run", "./streamlit.py"]