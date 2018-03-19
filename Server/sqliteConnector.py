import sqlite3
import binascii
'''
Functions include:

getNodeList() returns nodeList
getSecret(node) returns secret
getNodeID(macAddr) returns nodeID
getPSK(macAddr) returns PSK
getAddressing(node) returns dictionary
storeCookie(cookie, macAddr)
storeSecret(nodeID, secret)
setPhase (macAddr, phase)
validateCookie(cookie, macAddr) returns True or False
checkPhase(macAddr, phase) returns True or False
validatePSK(macAddr, PSK) returns True or False
checkACL(src, dst, service) returns True or False

'''


# get functions, when no entry in DB, return None(???)

def getNodeList():
	conn = sqlite3.connect('test2.db')
	nodeList = []
	cursor = conn.execute("SELECT * from Addressing")

	for row in cursor:
	   nodeID = row[0]
	   nodeList.append(nodeID)

	conn.close()

	return nodeList


def getSecret(node):
	conn = sqlite3.connect('test2.db')
	secretConn = conn.execute("SELECT * from Secret where nodeID = ?",(node,))
	secretRow = secretConn.fetchone()
	secret = secretRow[1]

	conn.close()

	return secret

def checkSecret(secret,macAddr):
	nodeID = getNodeID(macAddr)
	DBsecret = getSecret(nodeID)
	print("nodeID is: ",nodeID)
	print("DBsecret is: ",DBsecret)
	print("secret is: ",secret)
	if(DBsecret==secret):
		return True
	else:
		return False

def getNodeID(macAddr):
	conn = sqlite3.connect('test2.db')
	nodeConn = conn.execute("SELECT * from NodeID where phyAddress = ?",(macAddr,))
	nodeRow = nodeConn.fetchone()
	nodeID = nodeRow[1]

	conn.close()
	print("returning: ",nodeID)
	return nodeID


def getPSK(macAddr):
	conn = sqlite3.connect('test2.db')
	PSKConn = conn.execute("SELECT * from PSK where phyAddress = ?",(macAddr,))
	PSKRow = PSKConn.fetchone()
	PSK = PSKRow[1]

	conn.close()

	return PSK


def getAddressing(node):
	AddDict = {'Infra': '', 'InfrAdd': ''}
	conn = sqlite3.connect('test2.db')
	AddConn = conn.execute("SELECT * from Addressing where nodeID = ?",(node,))
	AddRow = AddConn.fetchone()
	if not (AddRow == None):
		AddDict['Infra'] = AddRow[2]
		AddDict['InfrAdd'] = AddRow[3]

	conn.close()

	return AddDict


def storeCookie(cookie, macAddr):
	print("SC mac:",macAddr)
	conn = sqlite3.connect('test2.db')
	c=conn.cursor()
	cookie=binascii.hexlify(cookie).decode()

	data = [macAddr, 0, cookie, macAddr]


	c.execute("UPDATE Phase set cookie = ? WHERE phyAddress = ?",(cookie,macAddr))
	#c.execute("INSERT INTO Phase VALUES (?,?,?)", data)

	conn.commit()

	conn.close()


def storeSecret(secret,macAddr):
	conn = sqlite3.connect('test2.db')
	nodeID = getNodeID(macAddr)
	c=conn.cursor()

	c.execute("UPDATE Secret set secret = ? WHERE nodeID = ?",(secret,nodeID))

	#data = [nodeID, secret]

	#c.execute("INSERT INTO Secret VALUES (?,?)", data)

	conn.commit()

	conn.close()

# def storeSecret(nodeID, secret):
# 	conn = sqlite3.connect('test2.db')
# 	c=conn.cursor()

# 	data = [nodeID, secret]

# 	c.execute("INSERT INTO Secret VALUES (?,?)", data)

# 	conn.commit()

# 	conn.close()


def setPhase (macAddr, phase):
	conn = sqlite3.connect('test2.db')
	c=conn.cursor()

	c.execute("UPDATE Phase SET phaseNum = ? WHERE phyAddress = ?", (phase,macAddr))

	conn.commit()

	conn.close()


def validateCookie(cookie, macAddr):
	conn = sqlite3.connect('test2.db')
	DBCookie = None
	cookieConn = conn.execute("SELECT * from Phase where phyAddress = ?",(macAddr,))
	cookieRow = cookieConn.fetchone()
	if not (cookieRow == None):
		DBCookie = cookieRow[2]

	conn.close()

	if (DBCookie == cookie):
	    return True
	else:
	    return False

def checkPhase(macAddr, phase):
	print("searching: ",macAddr)
	conn = sqlite3.connect('test2.db')
	DBPhase = None
	PhaseConn = conn.execute("SELECT * from Phase where phyAddress = ?",(macAddr,))
	PhaseRow = PhaseConn.fetchone()
	if not (PhaseRow == None):
		DBPhase = PhaseRow[1]

	conn.close()

	if (DBPhase == phase):
		print('correct phase')
		return True
	else:
		print(DBPhase,"not",phase)
		return False


def validatePSK(macAddr, PSK):
	conn = sqlite3.connect('test2.db')
	DBPSK = None
	print("looking for: ",macAddr)
	PSKConn = conn.execute("SELECT * from PSK where phyAddress = ?",(macAddr,))
	PSKRow = PSKConn.fetchone()
	if not (PSKRow == None):
		DBPSK = PSKRow[1]

	conn.close()
	print("DBPSK is: ",DBPSK)
	print("PSK is: ",PSK)
	if (DBPSK == PSK):
	    return True
	else:
	    return False


def checkACL(src, dst, service):
	conn = sqlite3.connect('test2.db')
	ACLConn = conn.execute("SELECT * from ACL where source =? AND destination = ? AND service = ?", (src, dst, service))
	ACLRow = ACLConn.fetchone()

	conn.close()

	if not(ACLRow == None):
	    return True
	else:
	    return False













