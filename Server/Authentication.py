import sqliteConnector
import Authorization
import binascii
from Crypto.Hash import MD5



def SecretQuery(node):
	#Gets the node's secret from the DB
	secret = sqliteConnector.getSecret(node)

	return secret


def secretCheck(parsePacket):
	#Gets secret, if a secret is returned, do HMAC Check
	#If no secret, then return False (not authenticated)
	secret = SecretQuery((parsePacket['src'])[0])
	if not (secret == None):
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
	else:
		return False

def Authenticate(parsePacket):
	print("I AM BEING AUTHENTICATED...")
	authenticated = secretCheck(parsePacket)
	print("I AM AUTHENTICATED: ", authenticated)
	#return authenticated

	#If it has passed authentication (same HMAC), it will redirect parsed packet to Authorization
	if (authenticated):
		Authorization.Authorize(parsePacket)