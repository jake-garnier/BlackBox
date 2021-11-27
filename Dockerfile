FROM python:3.7-slim

EXPOSE 5000/tcp

WORKDIR /app

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc  -y

COPY requirements.txt .
# RUN python -m venv venv
# RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/"

COPY flaskw ./flaskw
COPY instance ./instance

CMD [ "python", "./flaskw/__init__.py" ]