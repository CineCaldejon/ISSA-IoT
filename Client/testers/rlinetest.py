import time
def newReadLine(zb,timeout):
	startTime = time.time()
	eol = b'\r\n'
	leneol = len(eol)
	line = bytearray()
	while True:
		c = zb.read(1)
		if (c):
			line += c
			if line[-leneol:] == eol:
				print('eol')
				break
		curTime = time.time()
		if(curTime-startTime>=timeout):
			break
		#else:
	#	break
	return bytes(line)