import sqliteConnector
import Authentication

def Identification(packet):
	headerList = [b'\x00', b'\x01'] #possible values for header

	print("RECEIVED PACKET: ", packet)
	print("IDENTIFICATION MODULE")

	header = packet[0:1]


	#Checks if the header is valid. 
	#If valid, redirects to parseHandshake if it a handshake packet
	#If valid, redirects to parseService if it s a service packet
	if (header in headerList):
		if(header == b'\x00'):
			parseHandShake(packet)	
		elif(header == b'\x01'):
			parsePacket = parseService(packet)
			#if parseService does NOT return invalid = 1, means packet follows valid service format
			#Redirects packet to Authentication Module
			if not (parsePacket == 1):
				print("I HAVE A VALID SERVICE PACKET FORMAT")
				parsePacket['Header'] = header
				Authentication.Authenticate(parsePacket)

def parseHandshake(packet):
	#phaseList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04'] #possible values for handshake phase
	shakePhase = packet[1:2]

def parseService(packet):
	print("I AM A SERVICE PACKET")
	servList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04'] #possible values for service type
	servType = packet[1:2]
	parsePacket = {'Header': '', 'Type': '', 'src': '', 'dst': '', 'Payload': '', 'HMAC': ''} #dictionary contains hex values
	invalid = 0

	#If extracted service Type is valid, continue parsing
	if (servType in servList):

		srcNode = packet[2:3]
		dstNode = packet[3:4]

		#Check if srcNode and dstNode are already in the Addressing Table (i.e. they are already part of the overlay)
		if not (validateNode(srcNode[0])):
			invalid = 1
		if not (validateNode(dstNode[0])):
			invalid =1

		#If srcNode and dstNode are valid, continue parsing and define dictionary items
		if not (invalid):
			hmac = packet[-16:]
			payload = packet[4:-16]

			parsePacket['Type'] = servType
			parsePacket['src'] = srcNode
			parsePacket['dst'] = dstNode
			parsePacket['Payload'] = payload
			parsePacket['HMAC'] = hmac

			return parsePacket
	else:
		invalid = 1

	if(invalid):
		return invalid

	
def validateNode(nodeID):
	#Gets list of authenticated nodes from DB
	nodeList = sqliteConnector.getNodeList()

	#if nodeID given is in the list of authenticated nodes, return True, else return False
	if (nodeID in nodeList):
		valid = True
	else:
		valid = False

	return valid


   


import binascii
from Crypto.Hash import MD5


header = b'\x01\x00\x07\x2c\x04\x12\xff'
secret = 'HkdW54vs4FrSUS2Y'
temp = header + secret.encode()
ht = MD5.new()
ht.update(temp)
final = ht.hexdigest()
packet = header + bytes.fromhex(final)

Identification(packet)
#packet = b'\x01\x00\x07\x2c\x04\x12\xff\xb1\xfb\xe7\xf1\xe3\x02\xf1\xb3\x13\xa3\xca\xfc\x1d\xff\x14\xfe'
#packet2 = b'\x02\x00\x07\x2c\x04\x12\xff\xb1\xfb\xe7\xf1\xe3\x02\xf1\xb3\x13\xa3\xca\xfc\x1d\xff\x14\xfe'
#Identification(packet2)



