import time
import logging

LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "


def print_and_log(text, error=False):
    print(text)
    if error:
        logging.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logging.info(time.strftime(LOG_TIME_FORMAT) + text)