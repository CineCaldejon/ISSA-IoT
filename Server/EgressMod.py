import sqliteConnector
from Crypto.Hash import MD5
import binascii
from transceive import getZb
from transceive import WF_transmit
import handValidator
import time

def InfraQuery(nodeID):
	Infra = sqliteConnector.getAddressing(nodeID)

	return Infra

def Encapsulator(parsePacket):
	print("I AM BEING ENCAPSULATED")
	Infra = InfraQuery((parsePacket['dst'])[0])
	print("dest is :",parsePacket['dst'][0])
	secret = sqliteConnector.getSecret((parsePacket['dst'])[0])
	print("secret is",secret)
	data = b''
	for key, value in parsePacket.items():
		if (key != 'HMAC'):
			data = data + value

	packet = concatHmac(data, secret)

	return packet


def concatHmac(data,secret): # use packet as data
	ht = MD5.new()
	temp = data
	ht.update(data+secret.encode())
	buff = ht.hexdigest()
	concated = data + bytes.fromhex(buff)

	return concated

def handEgress(packet):
	print("handEgress: TO BE SENT OUT: ", packet)
	zb = getZb()
	eol= b'\r\n'
	time.sleep(4)
	zb.write(packet+eol)
	WF_transmit(packet)
	handValidator.checkHandshake(packet)

def Egress(parsePacket):
	packet = Encapsulator(parsePacket)
	print("TO BE SENT OUT: ", packet)
	zb = getZb()
	eol= b'\r\n'
	time.sleep(4)
	zb.write(packet+eol)
	WF_transmit(packet)