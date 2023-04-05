import socket

IP, PORT = "0.0.0.0", 8820
END_MSG = "Quit"

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))

server_socket.listen()
print("Server is up and running")

client_socket, client_address = server_socket.accept()
print(f"Client {client_address} connected")

while True:
    # Echo back data to client, if not END_MSG
    data = client_socket.recv(1024).decode()
    print(f"Client sent: {data}")
    if data == END_MSG:
        client_socket.send("Bye".encode())
        break
    client_socket.send(data.encode())

client_socket.close()
server_socket.close()
