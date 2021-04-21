# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
import os
from flask import Flask, request, jsonify, redirect
from instance_mgr import InstanceManager
from piddy_exception import PiddyurlException
from hash_gen import HashGenerator
from db import DBManagerHbase
from cache_mgr import CacheManager
from log_manager import LogManager

# global instances
instance_mgr = InstanceManager()
db_mgr = DBManagerHbase()
cache_mgr = CacheManager()
log_mgr = LogManager()

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.before_first_request
def before_first_request_func():
    log_mgr.getLogger().info("Initialized instance")


@app.errorhandler(PiddyurlException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/create')
def create_url():
    """Return a friendly HTTP greeting."""
    # Check whether the database has one such entry
    url_name = request.args.get('url', default='*', type=str)
    user_id = request.args.get('user', default='*', type=str)

    # validate the url and the user name
    if url_name == '*':
        raise PiddyurlException('No URL is passed')
    if url_name == '*':
        raise PiddyurlException('No user id is passed')

    # get the instance
    instance_id = instance_mgr.getInstanceID()
    latest = instance_mgr.getLatest()

    # check if it exists in db
    url_map = db_mgr.checkEntry(url_name, user_id)
    log_mgr.getLogger().info(url_map)
    if url_map is not None:
        updated_url = 'http://' + request.host + '/' + url_map['map_url']
        return jsonify({'status': 'success', 'url': url_name, 'piddyurl': updated_url})

    # generate the hash
    new_hash = HashGenerator.generateNext(instance_id, latest)

    # update the entry into db
    instance_mgr.updateLatest(new_hash)
    db_mgr.createEntry(url_name, user_id, new_hash)

    updated_url = 'http://' + request.host + '/redirect?url=' + new_hash
    return jsonify({'status': 'success', 'url': url_name, 'piddyurl': updated_url})


@app.route('/delete')
def delete_url():
    """Return a friendly HTTP greeting."""
    return 'Not implemented!'


@app.route('/')
def default_url():
    return "welcome to piddyurl"


# @app.route('/', defaults={'path': ''})
@app.route('/redirect')
def redirect_url():
    url_name = request.args.get('url', default='*', type=str)
    log_mgr.getLogger().info('redirect-page with the URL:  ' + url_name)
    if url_name == '*':
        raise PiddyurlException('No URL is passed')

    # check the cache
    url = cache_mgr.get(url_name)
    if url:
        log_mgr.getLogger().info('redirect-page found from the cache:  ' + url_name + ':' + url)
        return redirect(url)

    url = db_mgr.findMap(url_name)
    log_mgr.getLogger().info(url)
    if url:
        cache_mgr.put(url_name, url['url'])
        return redirect(url['url'])
    return jsonify({'status': 'fail', 'url': url_name, 'reason': 'not found'})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\saiba\\system_design_projects\\tinyurl\\key.json'

    app.run(host='0.0.0.0', port=5000, debug=True)

# [END gae_python38_app]
