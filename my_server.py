

from flask import Flask
app=Flask(__name__)

@app.route("/")
def hello():
    return '<h1>Home page</h1>'

@app.route("/create")
def create(url,dev_key):
    return 'aaaa'

@app.route("/delete")
def delete(url,dev_key):
    return ''

app.run(host='0.0.0.0',port=80)


