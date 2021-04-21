import datetime
import os

from google.cloud import datastore
# from piddy_exception import PiddyurlException
import happybase


class DBManagerHbase:
    def __init__(self):
        self.connection_pool = None

        self.hostname = os.environ.get('HBASE_HOST', 'db')
        self.urlmap_table_name = 'piddyurl_urlmap'
        self.urlset_table_name = 'piddyurl_urlset'

    def __connect(self):
        if not self.connection_pool:
            self.connection_pool = happybase.ConnectionPool(1, host=self.hostname)
            with self.connection_pool.connection() as con:
                # create table
                try:
                    con.create_table(self.urlmap_table_name, {'cf1': dict()})
                    con.create_table(self.urlset_table_name, {'cf1': dict()})
                except Exception as ex:
                    pass

    def createEntry(self, url_name, user_id, new_key):

        self.__connect()
        with self.connection_pool.connection() as con:
            # add in the url map (new_key => old url )
            new_urlmap_entry = {
                b'cf1:exp_date': str(datetime.datetime.now()).encode('ascii'),
                b'cf1:url': url_name.encode('ascii'),
                b'cf1:user_id': user_id.encode('ascii')
            }
            url_map = con.table(self.urlmap_table_name)
            url_map.put(new_key.encode('ascii'), new_urlmap_entry)

            # add in the urlset (old url=> new key)
            new_urlset_entry = {
                b'cf1:map_url': new_key.encode('ascii')
            }
            url_set = con.table(self.urlset_table_name)
            key_name = url_name + user_id
            url_set.put(key_name.encode('ascii'), new_urlset_entry)

    def checkEntry(self, url_name, user_id):
        self.__connect()
        with self.connection_pool.connection() as con:
            url_set = con.table(self.urlset_table_name)
            row = url_set.row((url_name + user_id).encode('ascii'))
            if len(row):
                new_dict = {'map_url': row[b'cf1:map_url'].decode('utf-8')}
                return new_dict
            else:
                return None

    def findMap(self, mapped_url):
        self.__connect()
        with self.connection_pool.connection() as con:
            url_map = con.table(self.urlmap_table_name)
            row = url_map.row(mapped_url.encode('ascii'))
            if len(row):
                new_dict = {'url': row[b'cf1:url'].decode('utf-8'),
                            'exp_date': row[b'cf1:exp_date'].decode('utf-8'),
                            'user_id': row[b'cf1:user_id'].decode('utf-8')}
                return new_dict
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
