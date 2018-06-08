import mq_clientHandshake
from Crypto.Hash import MD5
secret,node = mq_clientHandshake.exeHand('MQdW54vs4FrSUS2Y')

def overTest(dest,payload):
	global secret
	global node
	header = b'\x01\x00'+node +dest +payload
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	mq_clientHandshake.publish(packet)

print("my secret is:",secret)
print("my node is:",node[0])

overTest(b'\x28',b'lumos')