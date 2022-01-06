FROM 3.7-alpine

COPY blackbox_requirements.txt ./
RUN pip install -r blackbox_requirements.txt 

COPY app.py ./
COPY test.py ./

CMD ["app.handler"]  