def newReadLine(zb):
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
		#else:
	#	break
	return bytes(line)