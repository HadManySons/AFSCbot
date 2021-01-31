FROM python:3.8.3-alpine3.12
RUN apk update
RUN apk add bash
RUN apk add vim
COPY requrements.txt /app
COPY AuthDelete.py /app
RUN pip3.8 install -r /src/requirements.txt
WORKDIR /app
CMD ["python", "./AuthDelete.py"]
