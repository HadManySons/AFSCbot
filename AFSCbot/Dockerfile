FROM python:3.9.1-alpine3.12

RUN apk update
RUN apk add bash
RUN apk add vim

WORKDIR /app

RUN mkdir -p /app/csv_files
COPY ./csv_files/ /app/csv_files

WORKDIR /app
COPY requirements.txt .
COPY helper_functions.py .
COPY main.py .
COPY process_comment.py .
COPY read_csv_files.py .
COPY setup_bot.py .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
