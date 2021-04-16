import datetime
from google.cloud import datastore
from piddy_exception import PiddyurlException


class DbManager:

    def __init__(self):
        self.client = None

    def createEntry(self, url_name, user_id, new_key):
        if not self.client:
            self.client = datastore.Client()

        with self.client.transaction():
            url_map = datastore.Entity(self.client.key('URL_MAP', new_key))
            url_map.update(
                {
                    'exp_date': datetime.datetime.now(),
                    'url': url_name,
                    'user_id': user_id
                }
            )
            self.client.put(url_map)
            url_set = datastore.Entity(self.client.key('URL_SET', url_name+user_id))
            url_set.update(
                {
                    'map_url': new_key
                }
            )
            self.client.put(url_set)

    def checkEntry(self, url_name, user_id):
        if not self.client:
            self.client = datastore.Client()

        return self.client.get(self.client.key('URL_SET', url_name+user_id))

    def findMap(self, mapped_url):
        if not self.client:
            self.client = datastore.Client()

        return self.client.get(self.client.key('URL_MAP', mapped_url))

