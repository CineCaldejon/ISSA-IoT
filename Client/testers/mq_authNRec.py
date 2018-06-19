import mq_clientHandshake
import ReceiveV2
import pika
import binascii
import time
from Crypto.Hash import MD5
t0 = time.time()
secret,node = mq_clientHandshake.exeHand('MQdW54vs4FrSUS2Y')
t1 = time.time()
print("auth time is: ",t1-t0)
ReceiveV2.SetCreds(secret,node)

connection = None
t0 = None
t1 = None
def isMyPull(packet):
	dstNode = packet[3:4]
	print("DEBUG: isMyPull packet: ",binascii.hexlify(packet))
	if(packet[1:2]==b'\x02' and packet[3:4]==dstNode):
		return True
	else:
		print("DEBUG: isMyPull False: ",binascii.hexlify(packet[1:2]), " not ",binascii.hexlify(dstNode))
		return False	

def on_timeout():
	print("timeout reached")
	global connection
	connection.close()

def callback(ch, method, properties, body):
	validPacket = ReceiveV2.Receive(body)
	if(validPacket and isMyPull(validPacket)):
		print("pulled Data is: ",binascii.hexlify(body))
		parsePull(body)
		#do something about the reply
		ch.stop_consuming()

def pullRequest(packet):
	global connection
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_clientHandshake.BROKER))
	connection.add_timeout(24,on_timeout)
	channel = connection.channel()
	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue

	channel.queue_bind(exchange='pullData',queue=queue_name)
	channel.basic_consume(callback,queue=queue_name,no_ack=True)
	channel.basic_publish(exchange='serverHand',routing_key='',body=packet)
	channel.start_consuming()

def pullTest(dest,payload):
	global t0
	t0 = time.time()
	global secret
	global node
	header = b'\x01\x01'+node +dest +payload
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	pullRequest(packet)
	#mq_clientHandshake.publish(packet)

def parsePull(packet):
	global t1
	payload = packet[4:5]
	print("pulled data is: ",payload[0])
	t1 = time.time()

	print("time is: ",t1-t0)


pullTest(b'\x12',b'temp')