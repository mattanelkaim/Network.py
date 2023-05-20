"""
A simple UDP echo server, uses checksum
"""
import socket
import random

IP, PORT = "0.0.0.0", 8821
BUFFER_SIZE = 1024
CHECKSUM_LEN = 16  # 16 bits
TIMEOUT_IN_SECONDS = 10
CHECKSUM_ERROR_MSG = "Bad checksum"


def special_sendto(conn: socket.socket, response: str, addr: tuple[str, int]) -> None:
    """
    A sending function provided by the course itself
    :param conn: The socket connection
    :param response: The data to send
    :param addr: The address to send to
    :return: None
    """
    fail = random.randint(1, 3)
    if not (fail == 1):
        conn.sendto(response.encode(), addr)
    else:
        print("Connection interrupted :(")


def calc_checksum(msg_data: str) -> str:
    """
    Sums all the ASCII values in a given string,
    then formats to a string with length 16
    :param msg_data: The string to calculate its checksum
    :return: The checksum
    """
    total = sum(ord(x) for x in msg_data)  # Sum of all ASCII chars
    return str(total).rjust(CHECKSUM_LEN, "0")  # Formats to a 16-length string


# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))
print("Server is listening...")

data = ""
while data != "EXIT":
    # Read messages from client
    client_msg, client_addr = server_socket.recvfrom(BUFFER_SIZE)
    client_msg = client_msg.decode()
    # Split checksum and data
    checksum, data = client_msg[:CHECKSUM_LEN], client_msg[CHECKSUM_LEN:]

    # Calculate checksum on server and validate data
    server_checksum = calc_checksum(data)
    if server_checksum == checksum:  # Data is ok
        print(f"Client sent: {data}")
    else:
        print(CHECKSUM_ERROR_MSG)
        data = CHECKSUM_ERROR_MSG  # Send this error to the client
        server_checksum = calc_checksum(CHECKSUM_ERROR_MSG)

    # Send back to the client
    response_msg = server_checksum + data
    special_sendto(server_socket, response_msg, client_addr)

server_socket.close()
