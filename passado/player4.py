import socket

# Player info:
PLAYER_IP = "127.0.0.1" 
PLAYER_PORT = 21257 
PLAYER_ADDRESS = (PLAYER_IP, PLAYER_PORT)

# Next player info:
NEXT_PLAYER_IP = "127.0.0.1"
NEXT_PLAYER_PORT = 21254
NEXT_PLAYER_ADDRESS = (NEXT_PLAYER_IP, NEXT_PLAYER_PORT)

MESSAGE = "TEST p4 > p1 ".encode('utf-8')

socket_sender =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


socket_player = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
socket_player.bind(PLAYER_ADDRESS)

while True:
    data, addr = socket_player.recvfrom(1024)
    print(f"data received: {data.decode('utf-8')}")
    socket_sender.sendto(MESSAGE, NEXT_PLAYER_ADDRESS)
