FROM python:3.8.3-alpine3.12

RUN apk update
RUN apk add bash

WORKDIR /app

#WORKDIR /app/csv_files
RUN mkdir -p /app/csv_files
COPY ./csv_files/ /app/csv_files

WORKDIR /app
COPY requirements.txt .
COPY helper_functions.py .
COPY main.py .
COPY process_comment.py .
COPY read_csv_files.py .
COPY setup_bot.py .

RUN pip3.8 install -r requirements.txt

CMD ["python", "main.py"]
