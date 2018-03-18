import sqliteConnector
from Crypto.Hash import MD5
import binascii

def AddressingQuery(nodeID):
	#Gets Infrastructure and Infrastructure Address of the node
	AddDict = sqliteConnector.getAddressing(nodeID)

	return AddDict



def Encapsulator(parsePacket):
	print("I AM BEING ENCAPSULATED")
	#Get infra and infra address of the destination node
	AddDict = AddressingQuery((parsePacket['dst'])[0])
	invalid = 0


	#There should be an entry in the addressing table by this point
	#as the dst node has been validated during parsing
	#This is for extra checking in case something went wrong with the addresses
	if not (len(AddDict) == 0):
		infra = AddDict['Infra']
		infrAdd = AddDict['InfrAdd']

		#Get destination's secret for generation of HMAC
		secret = sqliteConnector.getSecret((parsePacket['dst'])[0])
		if not (secret == None):
			data = b''
			for key, value in parsePacket.items():
				if (key != 'HMAC'): #take packet except hmac
					data = data + value

			packet = concatHmac(data, secret)

			return packet

		#If no secret, set as invalid
		else: 
			invalid = 1

	if (invalid):
		return invalid


def concatHmac(data,secret): 
	#Compute for hash then concatenate with the packet
	ht = MD5.new()
	temp = data
	ht.update(data+secret.encode())
	buff = ht.hexdigest()
	concated = data + bytes.fromhex(buff)

	return concated


def Egress(parsePacket):
	packet = Encapsulator(parsePacket)

	#If Encapsulator does not return the invalid flag, continue with Egress
	if not (packet == 1):
		print("TO BE SENT OUT: ", packet)
