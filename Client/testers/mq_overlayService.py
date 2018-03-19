import pika
from Crypto.Hash import MD5
BROKER = '192.168.1.4'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
channel = connection.channel()
channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
channel.exchange_declare(exchange='clientHand',exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='serverHand',queue=queue_name)


def WF_transmit(packet):
	channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)

def sendpacket():
	header = b'\x01\x00\x07\x2c\x04\x12\xff'
	secret = 'HkdW54vs4FrSUS2Y'
	temp = header + secret.encode()
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	return packet

WF_transmit(sendpacket())