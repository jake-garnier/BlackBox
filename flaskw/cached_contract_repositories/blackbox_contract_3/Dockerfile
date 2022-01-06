# FROM python:3.7
# FROM public.ecr.aws/lambda/python:3.8
FROM python:3.8-slim-buster

COPY requirements.txt ./
RUN pip install -r requirements.txt 

COPY app.py ./
COPY test.py ./

CMD ["app.lambda_handler"]  