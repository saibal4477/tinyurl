import datetime
import os

from google.cloud import datastore
# from piddy_exception import PiddyurlException
import happybase


class DBManagerHbase:
    def __init__(self):
        self.client = None
        self.url_map = None
        self.url_set = None

        self.hostname = os.environ.get('HBASE_HOST', 'db')
        self.urlmap_table_name = 'piddyurl_urlmap'
        self.urlset_table_name = 'piddyurl_urlset'

    def __connect(self):
        if not self.client:
            self.client = happybase.Connection(self.hostname)
            # create table
            try:
                self.client.create_table(self.urlmap_table_name, {'cf1':dict()})
                self.client.create_table(self.urlset_table_name, {'cf1':dict()})
            except Exception as ex:
                pass

            self.url_map = self.client.table(self.urlmap_table_name)
            self.url_set = self.client.table(self.urlset_table_name)

    def createEntry(self, url_name, user_id, new_key):
        if not self.client:
            self.__connect()
        new_urlmap_entry = {
            b'cf1:exp_date': str(datetime.datetime.now()).encode('ascii'),
            b'cf1:url': url_name.encode('ascii'),
            b'cf1:user_id': user_id.encode('ascii')
        }
        self.url_map.put(new_key.encode('ascii'), new_urlmap_entry)
        new_urlset_entry = {
            b'cf1:map_url': new_key.encode('ascii')
        }
        self.url_set.put(url_name.encode('ascii'), new_urlset_entry)

    def checkEntry(self, url_name, user_id):
        self.__connect()
        row = self.url_set.row(url_name.encode('ascii'))
        if len(row):
            return row#[b'map_url']
        else:
            return None

    def findMap(self, mapped_url):
        self.__connect()
        row = self.url_set.row(mapped_url.encode('ascii'))
        if len(row):
            return row#[b'url']
        else:
            return None


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
            url_set = datastore.Entity(self.client.key('URL_SET', url_name + user_id))
            url_set.update(
                {
                    'map_url': new_key
                }
            )
            self.client.put(url_set)

    def checkEntry(self, url_name, user_id):
        if not self.client:
            self.client = datastore.Client()

        return self.client.get(self.client.key('URL_SET', url_name + user_id))

    def findMap(self, mapped_url):
        if not self.client:
            self.client = datastore.Client()

        return self.client.get(self.client.key('URL_MAP', mapped_url))
