
import logging
import os

import logstash
import sys

class LogManager:
    def __init__(self, logger_type=''):
        logging.basicConfig()
        self.logger = logging.getLogger('piddyurl-logstash-logger')
        self.logger.setLevel(logging.INFO)

        if logger_type=='logstash':
            host=os.environ.get('LOGSTASH_HOST','logstash')
            port=int(os.environ.get('LOGSTASH_PORT','9500'))
            self.logger.addHandler(logstash.LogstashHandler(host, port, version=1))


    def getLogger(self):
        return self.logger

