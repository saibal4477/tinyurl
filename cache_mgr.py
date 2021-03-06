import redis
import os

from piddy_exception import PiddyurlException


class CacheManager:
    def __init__(self):
        self.client = None
        self.redis_host = os.environ.get('REDIS_HOST', 'cache')
        self.redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        self.redis_passwd = None

    def put(self, key, val):
        if not self.client:
            self.client = redis.Redis(host=self.redis_host, port=self.redis_port)
        self.client.set(key, val)

    def get(self, key):
        if not self.client:
            self.client = redis.Redis(host=self.redis_host, port=self.redis_port)

        return self.client.get(key)
