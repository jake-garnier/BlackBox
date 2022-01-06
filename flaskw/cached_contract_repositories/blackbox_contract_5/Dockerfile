FROM 3.7-alpine

COPY requirements.txt ./
RUN pip install -r requirements.txt 

COPY app.py ./
COPY test.py ./

CMD ["app.lambda_handler"]  