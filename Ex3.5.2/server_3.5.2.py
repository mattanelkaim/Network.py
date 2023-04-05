"""
A simple UDP echo server
"""
import socket
import random

IP, PORT = "0.0.0.0", 8821
BUFFER_SIZE = 1024
MAX_DIGITS_SERIAL = 4
MAX_SERIAL_NUM = 10_000
TIMEOUT_IN_SECONDS = 10


def special_sendto(conn: socket, response: str, client_address: tuple[str, int]) -> None:
    """
    A sending function provided by the course itself
    :param conn: The socket connection
    :type conn: socket
    :param response: The data to send
    :type response: str
    :param client_address: The address to send to
    :type client_address: tuple[str, int]
    :return: None
    """
    fail = random.randint(1, 3)
    if not (fail == 1):
        conn.sendto(response.encode(), client_address)
    else:
        print("Oops")


# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))

data = ""
while data != "EXIT":
    # Read messages from client
    client_msg, client_addr = server_socket.recvfrom(BUFFER_SIZE)
    data = client_msg.decode()
    print(f"Client sent: {data}")

    # Echo back to the client
    special_sendto(server_socket, data, client_addr)

server_socket.close()
