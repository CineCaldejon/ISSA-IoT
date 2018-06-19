import rsa
#from amqpstorm import Connection
import pika
from Crypto.Cipher import AES
from queue import Queue
import binascii
import time
# is this obsolete?
BROKER = '192.168.1.106'
handQueue=Queue()

def getPhase(packet):
	phase =-1
	phase = int.from_bytes(packet[1:2],byteorder='big')
	return phase

expectedPhase = 1
psk =""
secret = None
nodeID = None
connection = None
macAddr = ""

def callme(ch, method, properties, body):

	global expectedPhase
	global psk
	global secret
	global nodeID
	incomingPhase=getPhase(body)
	print("server sent: ",binascii.hexlify(body))
	if(expectedPhase==incomingPhase and incomingPhase==1):
		print("runningTwo")
		publish(phaseTwo(body))
		expectedPhase+=1
		#ch.stop_consuming()
	if(expectedPhase==incomingPhase and incomingPhase==2):
		print("runningThree")
		publish(phaseThree(body,psk))
		expectedPhase+=1
		#ch.stop_consuming()
	if(expectedPhase==incomingPhase and incomingPhase==3):
		print("runningFour")
		secret ,nxt = phaseFour(body)
		publish(nxt)
		expectedPhase+=1
		#ch.stop_consuming()
	if(expectedPhase==incomingPhase and incomingPhase==4):
		nodeID = phaseFive(body)
		#publish(phaseFive(body))
		expectedPhase+=1
		ch.stop_consuming()

def on_timeout():
	print("timeout reached")
	global connection
	connection.close()


def getCredentials():
	global secret
	global nodeID
	return secret,nodeID

def exeHand(pskey):
	global psk
	global connection
	psk=pskey
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	connection.add_timeout(24,on_timeout)
	channel = connection.channel()
	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange='clientHand',queue=queue_name)
	channel.basic_consume(callme,queue=queue_name,no_ack=True)
	channel.basic_publish(exchange='serverHand',routing_key='',body=phaseOne())
	channel.start_consuming()
	channel.stop_consuming()
	connection.close()
	secret, node = getCredentials()
	return secret,node

def publish(data):
	print("sending: :",binascii.hexlify(data))
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	channel = connection.channel()
	channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
	channel.basic_publish(exchange='serverHand',routing_key='',body=data)
	connection.close()

def receive():
	print("HALO DER")
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	channel = connection.channel()
	channel.queue_declare(queue='clientHand')
	method_frame , header, body = channel.basic_get(queue='clientHand')
	if(method_frame==None):
		print("empty")
	#while(method_frame==None):#DOES NOT WORK
		#print("i am None")
		#method_frame , header, body = channel.basic_get(queue='clientHand')
	if method_frame.NAME == 'Basic.GetEmpty':
		connection.close()
		return ''
	else:
		channel.basic_ack(delivery_tag=method_frame.delivery_tag)
		connection.close()
		print("receive: ",body)
		return body

def handshakeHub(ch, method, properties, body):
	print('serverReplied')
	handQueue.put(body)
	ch.stop_consuming()

def wf_executeHandshake(psk):
	secret = None
	nodeID = None
	p1 = phaseOne()
	print("sending: ",p1)
	publish(p1)
	p2 = receive()
	print('starting phase 2')
	p3 = phaseTwo(p2)
	print("sending: ",p3)
	publish(p3)
	p4 = receive()
	print('starting phase 3')
	p5 = phaseThree(p4,psk)
	print("sending: ",p5)
	publish(p5)
	p6 = receive()
	secret,p7 = phaseFour(p6,psk)
	p8 = receive()
	nodeID = phaseFive(p8)
	return (secret,nodeID)
def phaseOne():
	global macAddr
	header=b'\x00\x00'
	packet=header+macAddr
	return packet

def phaseTwo(packet):
	header=b'\x00\x01'
	cookie=packet[10:]
	return header+macAddr+cookie

def phaseThree(packet,psk):
	header = b'\x00\x02'
	#psk = "Sixteen Byte key" #TODO: fix
	derPubKey=packet[10:]
	pubKey=rsa.PublicKey.load_pkcs1(derPubKey,format='DER')
	cypherText = rsa.encrypt(psk.encode(),pubKey)
	return header+macAddr+cypherText

def phaseFour(packet):
	global secret
	header = b'\x00\x03'
	#psk= "Sixteen Byte key"
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	cypher = packet[10:]
	secret = aesKey.decrypt(cypher)
	cypherText = aesKey.encrypt(secret)
	#print("my secret is :",secret)
	return secret,header+macAddr+cypherText

def phaseFive(packet):
	header = b'\x00\x04'
	#psk= "Sixteen Byte key"
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	cypher = packet[10:]
	nodeID = aesKey.decrypt(cypher)
	#print("my node id is :",nodeID)
	return nodeID[0:1]

#x,y = exeHand("HkdW54vs4FrSUS2Y")
#print("my secret is: ",x)
#print("my node ID is: ",y[0])
#while True:
#	print(receive())