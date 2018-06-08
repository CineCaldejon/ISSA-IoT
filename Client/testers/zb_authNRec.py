import rsa
from Crypto.Cipher import AES
import serial
import binascii
import time
import ReceiveV2
import sys
from Crypto.Hash import MD5
import threading
import rlinetest
import zbclient_tranceiver

#secret=None
#node=None
secret=b''
node=b''

def publish(data):
	zb  = zbclient_tranceiver.getZb()
	eol = b'\r\n'
	print("sending(len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	time.sleep(4)	
	zb.write(data+eol)

def forMe(packet):
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	Pmac = packet[2:10]
	#print("Pmac: ",Pmac)
	if(macAddr==Pmac):
		return True
	else:
		print("Pmac: ",binascii.hexlify(Pmac))
		print("macAddr: ",binascii.hexlify(macAddr))
		return False

def receive():
	zb  = zbclient_tranceiver.getZb()
	data = rlinetest.newReadLine(zb,12)
	print("received: (len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	if not (data==None):
		if(forMe(data)):
			return data[:-2]
	return None

def zb_executeHandshake(psk):
	secret = None
	nodeID = None
	p1 = phaseOne()
	publish(p1)
	p2 = receive()
	p3 = phaseTwo(p2)
	publish(p3)
	p4 = receive()
	p5 = phaseThree(p4,psk)
	publish(p5)
	p6 = receive()
	secret,p7 = phaseFour(p6,psk)
	publish(p7)
	p8 = receive()
	nodeID = phaseFive(p8,psk)
	return (secret,nodeID)
def phaseOne():
	header=b'\x00\x00'
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	infra = b'\x01'
	packet=header+macAddr+infra
	return packet

def phaseTwo(packet):
	header=b'\x00\x01'
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	cookie=packet[10:]
	infra=b'\x01'
	print("p2 pack:",binascii.hexlify(packet))
	print("p2 cook: ",binascii.hexlify(cookie))
	return header+macAddr+infra+cookie

def phaseThree(packet,psk):
	header = b'\x00\x02'
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	#psk = "Sixteen Byte key" #TODO: fix
	print("p3 packet is:",binascii.hexlify(packet))
	derPubKey=packet[10:]
	print("pubKey is: ",binascii.hexlify(derPubKey))
	pubKey=rsa.PublicKey.load_pkcs1(derPubKey,format='DER')
	cypherText = rsa.encrypt(psk.encode(),pubKey)
	print("cypherText is:",binascii.hexlify(cypherText))
	return header+macAddr+cypherText

def phaseFour(packet,psk):
	global secret
	header = b'\x00\x03'
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	#psk= "Sixteen Byte key"
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	cypher = packet[10:]
	secret = aesKey.decrypt(cypher)
	cypherText = aesKey.encrypt(secret)
	#print("my secret is :",secret)
	return (secret,header+macAddr+cypherText)

def phaseFive(packet,psk):
	header = b'\x00\x04'
	macAddr = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
	#psk= "Sixteen Byte key"
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	cypher = packet[10:]
	nodeID = aesKey.decrypt(cypher)
	print("decrypted is: ",nodeID)
	return nodeID[0:1]

#secret = b'83A4BF6F17C447A5'
#node = b'\x27'

secret,node = zb_executeHandshake("HkdW54vs4FrSUS2Y")
ReceiveV2.SetCreds(secret,node)
print("my secret is: ",secret)
print("my node ID is: ",node[0])


def overTest(dest,payload):
	global secret
	global node
	header = b'\x01\x00'+node +dest +payload
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	publish(packet)

#overTest(b'\x2c',b'lumos')

def isMyPull(packet):
	if(packet[1:2]==b'\x02'):
		return True
	else:
		return False	

def pullReceive():
	startTime = time.time()
	zb  = zbclient_tranceiver.getZb()
	buff = rlinetest.newReadLine(zb,12)
	if not (buff==b''):
		data = ReceiveV2.Receive(buff[:-2])
	curTime = time.time()
	while(curTime - startTime <24):
		buff = rlinetest.newReadLine(zb,12)
		if not(buff==b''):
			print('buff is',buff[:-2])
			data = ReceiveV2.Receive(buff[:-2])
			if(isMyPull(data)):
				return data[:-2]
		curTime = time.time()
	return None


def pullService(dest,payload):
	global secret
	global node
	header = b'\x01\x01'+node +dest +payload
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	publish(packet)
	reply = pullReceive()
	if(reply==None):
		print("pull request timed out")
		return None
	return reply

def recPackets():
	while True:
		zb = serial.Serial(SERPORT, timeout=1)
		try:
			data = zb.readline()
			Receive.Receive(data[:-2])
		except KeyboardInterrupt:
			sys.exit()
		print('endRec')
		zb.close()

def parsePull(packet):
	payload = packet[4:5]
	print(payload[0])

parsePull(pullService(b'\x28',b'temp'))

#print("pull reply is: ",pullService(b'\x28',b'temp'))


#while True:
#	print(receive())