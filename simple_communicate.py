import bluetooth
DEGREES_PROMPT_MESSAGE = "Degrees: "
bd_addr = "00:14:03:06:75:C2" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

prompt_msg = DEGREES_PROMPT_MESSAGE
while True:
	x = input()
	sock.send(x)

