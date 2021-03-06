import binascii
import pika
import time
import threading
import serial

import uni_handMod
import ServIngress

import transceive

def zbStart():
	transceive.zbRecv()

def mqStart():
	transceive.mqRecv()

def handTransmit(packet):#junk code
	zb  = tranceive.getZb()
	#zb  = serial.Serial(SERPORT)
	print("sending(len:",len(binascii.hexlify(packet)),") :",binascii.hexlify(packet))
	eol= b'\r\n'
	time.sleep(4)
	zb.write(packet+eol)
	channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)
	print("sent")

def parsePacket(packet):
	print("received: ",binascii.hexlify(packet))
	egress = uni_handMod.handshakeHub(packet)
	print("going to egress: ",egress)
	handTransmit(egress)
def ProcessPacketQueue():
	try:
		while True:
			packet = transceive.packetQueue.get()
			#parsePacket(packet)
			egress = ServIngress.Identification(packet)
			#handTransmit(egress)
			#parsePacket(packet) # send to parsing module
			transceive.packetQueue.task_done()
	except KeyboardInterrupt:
		print('interrupted!')
		exit()

t1 = threading.Thread(target = zbStart)
t1.daemon = True
t1.start()

t2 = threading.Thread(target = mqStart)
t2.daemon = True
t2.start()

t3 = threading.Thread(target = ProcessPacketQueue)
t3.start()