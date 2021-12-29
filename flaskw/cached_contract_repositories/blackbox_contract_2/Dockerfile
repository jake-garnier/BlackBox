FROM python:3.7

COPY app.py ./
CMD ["app.lambda_handler"]  

COPY test.py ./

COPY requirements.txt ./
RUN pip install -r requirements.txt 