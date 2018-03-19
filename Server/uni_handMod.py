from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import uuid
import rsa
import pika
import time
import threading
import serial
(pubkey,privkey) = rsa.newkeys(512)

import sqliteConnector

def handshakeHub(packet):
	print("hub packet:",binascii.hexlify(packet))
	
	#print("parse is: ",packet[1:2])
	phase = int.from_bytes(packet[1:2],byteorder='big')
	#phase = "{:02x}".format(ord(packet[1:2]))
	macAddr = packet[2:10]
	macAddr = binascii.hexlify(macAddr).decode()
	#print(phase)
	if(sqliteConnector.checkPhase(macAddr,phase)):#TODO: return true if valid false if invalid
		if(phase==0):
			print("phase one")
			sqliteConnector.setPhase(macAddr,phase+1)#TODO: set to next phase
			handPack=phaseOne(packet)
			print("handpack: ",handPack)
			return handPack
			#transmit(handPack)#TODO: broadcast? to all interface
		if(phase==1):
			print("phase two")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseTwo(packet)
			print("handpack: ",handPack)
			return handPack
			#transmit(handPack)
		if(phase==2):
			print("phase 3")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseThree(packet)
			print("handpack: ",handPack)
			return handPack
			#transmit(handPack)
		if(phase==3):
			print("phase 4")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseFour(packet)
			print("handpack: ",handPack)
			return handPack
			#transmit(handPack)

def randGen(string_length=10):
	random = str(uuid.uuid4())
	random = random.upper()
	random = random.replace('-','')
	return random[0:string_length]


def validateCookie(cookie,macAddr):
	return True


def phaseOne(packet):
	phase = packet[0:1]
	macAddr = packet[2:10]
	#print(binascii.hexlify(phase))
	#print(binascii.hexlify(macAddr))# NOTE: binascii is for printing only
	ht = MD5.new()
	salt = randGen(4)
	ht.update(macAddr)
	ht.update(salt.encode())
	cookie = bytes.fromhex(ht.hexdigest())
	sqliteConnector.storeCookie(cookie,binascii.hexlify(macAddr).decode())# TODO: store cookie for macAddr
	phaseHeaders= b'\x00\x01'
	nxtPacket = phaseHeaders+macAddr+cookie
	return nxtPacket


def phaseTwo(packet):
	print("P2 packet: ", binascii.hexlify(packet))
	cookie = packet[-16:]
	macAddr = packet[2:10]

	print("cookie: ",binascii.hexlify(cookie))
	print("macAddr: ",binascii.hexlify(macAddr))

	ht = MD5.new()
	ht.update(macAddr)
	buff = ht.hexdigest()
	phaseHeader=b'\x00\x02'

	if(sqliteConnector.validateCookie(binascii.hexlify(cookie).decode(),binascii.hexlify(macAddr).decode())):#TODO: return true if cookie and mac matches else return false
		exportKey = pubkey.save_pkcs1(format='DER')
		print("pubKey is: ",binascii.hexlify(exportKey))
		return phaseHeader+macAddr+exportKey
	else:
		return False


def phaseThree(payload):
	global privkey
	phaseHeader=b'\x00\x03'
	cypher = payload[10:]
	print("p3 cypher: ",binascii.hexlify(cypher))
	macAddr =payload[2:10]
	#macAddr = binascii.hexlify(macAddr).decode()
	decryptedKey = rsa.decrypt(cypher,privkey)
	print("THE DECRYPTED KEY IS :",decryptedKey)
	if(sqliteConnector.validatePSK(binascii.hexlify(macAddr).decode(),decryptedKey.decode())):#TODO: check if key and mac is valid
		aesKey = AES.new(decryptedKey,AES.MODE_ECB)
		secret = randGen(16)
		print("SENDING SECRET: ",secret)
		sqliteConnector.storeSecret(secret,binascii.hexlify(macAddr).decode())#TODO: store shared secret to secret table
		#print(type(secret.encode()))
		cypherSecret = aesKey.encrypt(secret.encode())
		#cypherSecret = aesKey.encrypt(pad(secret.encode(),16))
		return phaseHeader+macAddr+cypherSecret

def phaseFour(payload):
	macAddr = payload[2:10]
	print(macAddr)
	print(binascii.hexlify(macAddr).decode())
	cypher = payload[10:]
	psk = sqliteConnector.getPSK(binascii.hexlify(macAddr).decode())#TODO: get psk based on macaddr
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	secret = aesKey.decrypt(cypher).decode()
	if(sqliteConnector.checkSecret(secret,binascii.hexlify(macAddr).decode())):#TODO: check if secret is valid
		nodeid=sqliteConnector.getNodeID(binascii.hexlify(macAddr).decode())#TODO: get static node
		
		nodeid = str(nodeid).encode()
		#nodeid = binascii.hexlify(bytes([nodeid])).decode()
		print("P4 nodeid: ",nodeid)
		cypherNodeID = aesKey.encrypt(pad(nodeid, 16))
		header = b'\x00\x04'
		packet = header+macAddr+cypherNodeID
		return packet

