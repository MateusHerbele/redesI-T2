import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = "Hello, World!".encode('utf-8')

print(f"UDP target IP: {UDP_IP}")
print(f"UDP target port: {UDP_PORT}")
print(f"message: {MESSAGE}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))