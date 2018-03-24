import serial
from Crypto.Hash import MD5

def sendpacket():
	header = b'\x01\x00\x07\x2c\x04\x12\xff'
	secret = 'HkdW54vs4FrSUS2Y'
	temp = header + secret.encode()
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	eol = b'\r\n'
	zb = serial.Serial('COM4')
	zb.write(packet+eol)
	zb.close()

sendpacket()
# zb = serial.Serial('COM8')
# while True:
# 		header = b'\x01\x00\x07\x2c\x04\x12\xff'
# 		secret = 'HkdW54vs4FrSUS2Y'
# 		temp = header + secret.encode()
# 		ht = MD5.new()
# 		ht.update(temp)
# 		final = ht.hexdigest()
# 		packet = header + bytes.fromhex(final)
# 		eol = b'\r\n'
# 		zb.write(packet+eol)