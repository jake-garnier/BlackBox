FROM python:3.7

EXPOSE 5000/tcp

WORKDIR /app

# RUN export DOCKER_HOST="tcp://HOST:2375"

# RUN apk update 
# RUN apk add
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc  -y

COPY requirements.txt .
# RUN python -m venv venv
# RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/"

COPY flaskw /app/flaskw
COPY instance /app/instance

CMD [ "python", "/app/flaskw/__init__.py" ]