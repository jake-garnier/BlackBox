FROM python:3.7-slim

EXPOSE 5000/tcp

WORKDIR /app

COPY requirements.txt .
RUN python -m venv venv
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt

COPY flaskw ./flaskw
COPY instance ./instance

CMD [ "python", "./flaskw/__init__.py" ]