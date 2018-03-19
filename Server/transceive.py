import serial
import pika
from queue import Queue

BROKER = '192.168.1.4'
SERPORT = 'COM8'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
channel = connection.channel()
packetQueue = Queue()

zb = serial.Serial(SERPORT)
channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
channel.exchange_declare(exchange='clientHand',exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='serverHand',queue=queue_name)

def WF_transmit(packet):
	channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)

def getZb():
	global zb
	return zb

def callback(ch, method, properties, body):
	packetQueue.put(body)

def zbRecv():
	global testlock
	while True:
		data = zb.readline()
		packetQueue.put(data[:-2])

def mqRecv():
	channel.basic_consume(callback,queue=queue_name,no_ack=True)
	channel.start_consuming()

def handTransmit(packet):#junk code
	global zb
	#zb  = serial.Serial(SERPORT)
	print("sending(len:",len(binascii.hexlify(packet)),") :",binascii.hexlify(packet))
	eol= b'\r\n'
	time.sleep(4)
	zb.write(packet+eol)
	channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)