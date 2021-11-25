FROM public.ecr.aws/lambda/python:3.8

COPY app.py ./
CMD ["app.handler"]  

COPY requirements.txt ./
RUN pip install -r requirements.txt 