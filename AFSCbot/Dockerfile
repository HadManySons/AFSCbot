FROM python:3.8.3-alpine3.12
RUN apk update
RUN apk add bash
COPY ./AFSCbot/csv_files /src/csv_files
COPY ./AFSCbot/requirements.txt /src/requirements.txt
RUN pip3.8 install -r /src/requirements.txt
COPY ./AFSCbot/helper_functions.py /src/helper_functions.py
COPY ./AFSCbot/main.py /src/main.py
COPY ./AFSCbot/process_comment.py /src/process_comment.py
COPY ./AFSCbot/read_csv_files.py /src/read_csv_files.py
COPY ./AFSCbot/setup_bot.py /src/setup_bot.py
COPY ./AFSCbot/AuthDelete.py /src/AuthDelete.py
COPY ./AFSCbot/start.sh /src/start.sh
RUN chmod +x /src/start.sh
WORKDIR /src
CMD ["/src/start.sh"]