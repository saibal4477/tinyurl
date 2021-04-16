
from piddy_exception import PiddyurlException

class CacheManager:
    def __init__(self):
        self.client=None

    def put(self, key):
        if not self.client:
            self.client=memcache

    def get(self):
        return 1
