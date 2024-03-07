import time
import logging
from logging.handlers import RotatingFileHandler

LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "

logger = logging.getLogger("AFSCbot Rotating Log")
logger.setLevel(logging.INFO)
    
# add a rotating handler
handler = RotatingFileHandler("AFSCbot.log", maxBytes=2048000, backupCount=25)
logger.addHandler(handler)

def print_and_log(text, error=False):
    print(text)
    if error:
        logger.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logger.info(time.strftime(LOG_TIME_FORMAT) + text)


def has_number(string):
    for char in string:
        if char.isdigit():
            return True
    return False
