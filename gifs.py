import socket

IP = "120.85.6.28"  # GIF #1
PORT = 8281  # GIF 3
MSG = "my code works"  # GIF #2

# 800  # GIF #4

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # GIF #5
my_socket.sendto(MSG.encode(), (IP, PORT))
data = my_socket.recvfrom(1024)  # GIF #6

print(f"SERVER SENT: {data.decode()}")
