import serial
import Receive
import rlinetest
from queue import Queue
SERPORT = 'COM9'

servQueue = Queue()
zb = serial.Serial(SERPORT,timeout=1)

def getZb():
	global zb
	return zb

def zbRecv():
	while True:
		data = rlinetest.newReadLine(zb)
		validPack = ReceiveV2.Receive(data)
		if(validPack):
			print(validPack)
			servQueue.put(validPack)
		#data = zb.readline()
		zb.flush()


def transmit(packet):
	eol = b'\r\n'
	print("sending(len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	time.sleep(4)	
	zb.write(data+eol)