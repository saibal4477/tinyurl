
import pika
from flask import Flask
from flask import request

class KeyGenService:

    def __init__(self):
        self.host_ip_ = '34.121.61.90'
        self.key_queue_name_ = 'KEYS'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host_ip))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.key_queue_name, durable=True)
        return

    def assignKey(self):
        self.channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body.decode())
            # time.sleep(body.count(b'.'))
            print(" [x] Done")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=self.key_queue_name_, on_message_callback=callback)
        self.channel.start_consuming()
        return

    def genKey(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host_ip))
        channel = connection.channel()
        channel.queue_declare(queue=self.key_queue_name_)

        while True:
            new_key_name = self.newKey()
            channel.basic_publish(exchange='',
                                  routing_key=self.key_queue_name_,
                                  body=new_key_name)

        return

    def newKey(self) -> str:
        return 'a'


keygen=KeyGenService()
app = Flask(__name__)


@app.route('/newKey')
def newKey():
    return keygen.newKey()


