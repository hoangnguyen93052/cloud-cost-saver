import json
import os
import time
from flask import Flask, request, jsonify
import pika
from threading import Thread

app = Flask(__name__)

# Configuration for the RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
QUEUE_NAME = 'task_queue'


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message,
                          properties=pika.BasicProperties(delivery_mode=2, ))
    print(f" [x] Sent '{message}'")
    connection.close()


@app.route('/send', methods=['POST'])
def send():
    data = request.json
    message = data.get('message')
    send_message(message)
    return jsonify({"status": "Message sent", "message": message}), 200


def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))  # Simulate some work
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    t = Thread(target=consume_messages)
    t.start()
    app.run(host='0.0.0.0', port=5000)