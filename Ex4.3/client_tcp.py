import socket

IP, PORT = "loopback", 5555
END_MSG = "BYE"

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((IP, PORT))

data = ""
while data.upper() != END_MSG:
    data = input("Enter your message:\n")
    my_socket.send(data.encode())
    data = my_socket.recv(1024).decode()
    print(f"Server sent: {data}\n")

print("Closing ur socket")
my_socket.close()
