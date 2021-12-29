FROM python:3.7
# FROM public.ecr.aws/lambda/python:3.8

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
    apt-get install -y \
    autoconf \
    libtool \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt 

COPY app.py ./
COPY test.py ./

ENTRYPOINT ["npx", "aws-lambda-ric"]
CMD ["app.lambda_handler"]  