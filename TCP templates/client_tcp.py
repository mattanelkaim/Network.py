import socket

IP, PORT = "10.100.102.6", 8820
END_MSG = "Bye"

# Create a TCP socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((IP, PORT))

data = ""
while data != END_MSG:
    # Send user input to server, then print its response
    data = input("Enter your message\n")
    my_socket.send(data.encode())
    data = my_socket.recv(1024).decode()
    print(f"Server sent: {data}")

print("Closing ur socket")
my_socket.close()
