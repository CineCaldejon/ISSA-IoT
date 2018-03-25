#import RPi.GPIO as GPIO



def Push(payload):
	#GPIO.setmode(GPIO.BCM)
	#GPIO.setup(4, GPIO.OUT)

	#if(payload.decode() == 'lumos'):
	#	GPIO.ouput(4, 1)
	#else:
	#	GPIO.output(4, 0)
	print("PAYLOAD IS ", payload)

	#GPIO.cleanup()


#def PullReq(payload):

#def PullRep(payload):

#def DataSend(payload):

#def DataCollect(payload):


def Service(parsePacket):
	servType = parsePacket['Type']
	payload = parsePacket['Payload']

	if(servType == b'\x00'):
		Push(payload)
	elif(servType == b'\x01'):
		PullReq(payload)
	elif(servType == b'\x02'):
		PullRep(payload)
	elif(servType == b'\x03'):
		DataSend(payload)
	elif(servType == b'\x04'):
		DataCollect(payload)