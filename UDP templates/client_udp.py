import socket

IP, PORT = "127.0.0.1", 8821
BUFFER_SIZE = 1024

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send a message to server
client_socket.sendto("imma tell u a UDP joke".encode(), (IP, PORT))

# Get response from server
data, server_address = client_socket.recvfrom(BUFFER_SIZE)
print(f"Server sent: {data.decode()}")

client_socket.close()
