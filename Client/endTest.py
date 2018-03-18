import pika
import Receive

BROKER='192.168.1.4'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
channel = connection.channel()

channel.exchange_declare(exchange='clientHand',
                         exchange_type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='clientHand',
                   queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    #print(" [x] %r" % body)
    Receive.Receive(body)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

