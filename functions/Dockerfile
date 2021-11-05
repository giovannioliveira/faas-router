FROM python:3.8

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY router.py app.py

CMD [ "python3", "app.py"]