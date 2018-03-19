from Crypto.Hash import MD5

global nodeID
global secret


def Receive(packet):
	print("RECEIVED PACKET: ", packet)
	print("CHECKING IF THIS IS FOR ME...")

	headerList = [b'\x00', b'\x01'] #possible values for header
	header = packet[0:1]

	if (header in headerList):
		if(header == b'\x00'):
			parseHandShake(packet)

		elif(header == b'\x01'):
			parsePacket = parseService(packet)

			if not (parsePacket == 1):
				print("OMG IT'S FOR ME :>")
				parsePacket['Header'] = header
				check = HMACCheck(parsePacket)

def parseHandshake(packet):
	#phaseList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04'] #possible values for handshake phase
	shakePhase = packet[1:2]

def parseService(packet):
	print("RECEIVED A SERV PACKET")
	servList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04'] #possible values for service type
	servType = packet[1:2]
	parsePacket = {'Header': '', 'Type': '', 'src': '', 'dst': '', 'Payload': '', 'HMAC': ''} #dictionary contains hex values
	invalid = 0

	#If extracted service Type is valid, continue parsing
	if (servType in servList):

		srcNode = packet[2:3]
		dstNode = packet[3:4]

		if(dstNode[0] == nodeID):

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

	else:
		invalid = 1

	if (invalid):
		return invalid

def HMACCheck(parsePacket):
	print("HMAC CHECK")
	headers = b''
	for key, value in parsePacket.items():
		if (key != 'HMAC'): # take packet except hmac
			headers = headers + value
	Hash = parsePacket['HMAC'].hex() # get bytes literally
	temp = headers + secret.encode()
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	print("HASH COMPUTED: ",final)
	print("HASH RECEIVED: ", Hash)
	#If computed hash is same with received hash, it has passsed authentication
	if Hash == final:
		print("Packet is valid")
		return True
	#Else, it has not passed authentication
	else:
		print("Packet is invalid")
		return False



#header = b'\x01\x00\x07\x2c\x04\x12\xff'
nodeID = 44
secret = 'gHBKJDwsbKDsR4dq'
#temp = header + secret.encode()
#ht = MD5.new()
#ht.update(temp)
#final = ht.hexdigest()
#packet = header + bytes.fromhex(final)

#Receive(packet)





