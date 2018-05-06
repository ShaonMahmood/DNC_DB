FROM python:latest
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir /src
RUN mkdir /static
WORKDIR /src
ADD . /src
RUN pip install -r requirements.txt