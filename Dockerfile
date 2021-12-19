FROM python:3.7

EXPOSE 5000/tcp

WORKDIR /app

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc  -y

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/"

COPY flaskw /app/flaskw
COPY instance /app/instance

CMD [ "python", "/app/flaskw/__init__.py" ]