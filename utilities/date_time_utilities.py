import logging
import time

logger = logging.getLogger(__name__)

def epoch_to_date(epoch, date_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(date_format, time.localtime(epoch))

def current_epoch():
    return int(time.time())