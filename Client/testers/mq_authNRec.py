import mq_clientHandshake
import ReceiveV2
from Crypto.Hash import MD5
secret,node = mq_clientHandshake.exeHand('MQdW54vs4FrSUS2Y')
ReceiveV2.SetCreds(secret,node)

BROKER = 'localhost'

def isMyPull(packet):
	if(packet[1:2]==b'\x02'):
		return True
	else:
		return False	

def on_timeout():
	print("timeout reached")
	global connection
	connection.close()

def callback(ch, method, properties, body):
	validPacket = ReceiveV2.Receive(body)
	if(isMyPull(validPacket)):
		#do something about the reply
		ch.stop_consuming()

def pullRequest(packet):
	channel.basic_publish(exchange='serverHand',routing_key='',body=packet)
	channel.start_consuming()

connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
connection.add_timeout(24,on_timeout)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='clientHand',queue=queue_name)
channel.basic_consume(callback,queue=queue_name,no_ack=True)