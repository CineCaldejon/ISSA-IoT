import sqliteConnector
import time
def runTimer():
	while True:

		nodeTimers = sqliteConnector.getTimers() # TODO: fetch nodeTimers via: (nodeID,TTL)
		updatedTimers = []
		for timer in nodeTimers:
			nodeID = timer[0]
			isAlive = timer[1]
			if(isAlive == 1):
				updatedTimers.append((nodeID,0))
			else:
				sqliteConnector.killNode(nodeID) # TODO: execute dead node
		for timer in updatedTimers:	
			sqliteConnector.updateTimer(timer[0],timer[1]) # TODO: modify values one at a time
		time.sleep(20)