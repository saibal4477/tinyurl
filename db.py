from google.cloud import datastore


def createEntry(url_name,user_id):
    client = datastore.Client()
    with client.transaction():
        url_map = datastore.Entity(client.key("URL_MAP"))
        url_map.update(
            {
                'exp_date':  '2021-03-31 (11:17:00.000) UTC-7', 
                'mapped': '', 
                'orig': url_name,
                'user_id': user_id
            }
        )
        client.put(url_map)
        

