import sqliteConnector
import EgressMod

def Authorize(parsePacket):
	print("I AM BEING AUTHORIZED...")
	src = (parsePacket['src'])[0]
	dst = (parsePacket['dst'])[0]
	servType = parsePacket['Type']

	#Gets service type corresponding to the hex value
	if(servType == b'\x00'):
		service = "Push"
	elif(servType == b'\x01'):
		service = "PullReq"
	elif(servType == b'\x02'):
		service = "PullRep"
	elif(servType == b'\x03'):
		service = "DataSend"
	elif(servType == b'\x04'):
		service = "DataCollect"

	#Checks if there is an entry on the ACL Table
	#Existing entry means that the actions is permitted
	authorized = sqliteConnector.checkACL(src, dst, service)

	#return authorized

	#If the action is permitted, redirect packet to Egress Module
	if (authorized):
		print('I AM AUTHORIZED ', parsePacket, "\n")
		EgressMod.Egress(parsePacket)

	else:
		print("I AM NOT AUTHORIZED :( ")

