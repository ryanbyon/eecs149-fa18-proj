import bluetooth
import time
bd_addr = "00:14:03:06:74:D9" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))
data = ''
while 1:
	try:
		data += sock.recv(1024).decode('ascii')
		end = data.find("\n")
		if end != -1:
			rec = data[:end]
			print(str(data))
			data = data[end-1:]
	except KeyboardInterrupt:
		break


sock.close()


