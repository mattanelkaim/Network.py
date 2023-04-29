"""
Implementing timeouts & retransmissions and checksum in a UDP connection
"""
import socket
import random

IP, PORT = "127.0.0.1", 8821
BUFFER_SIZE = 1024
CHECKSUM_LEN = 16  # 16 bits
TIMEOUT_IN_SECONDS = 5


def special_sendto(conn: socket, response: str, addr: tuple[str, int]) -> None:
    """
    A sending function provided by the course itself, to simulate packet loss
    :param conn: The socket connection
    :type conn: socket
    :param response: The data to send
    :type response: str
    :param addr: The address to send to
    :type addr: tuple[str, int]
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
    :type msg_data: str
    :return: The checksum
    :rtype: str
    """
    total = sum(ord(x) for x in msg_data)  # Sum of all ASCII chars
    return str(total).rjust(CHECKSUM_LEN, "0")  # Formats to a 16-length string


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = ""  # Holds data and checksum
while data != "EXIT":
    # Get message from user and send to server
    data = input("Enter your message:\n")
    checksum = calc_checksum(data)
    msg = checksum + data

    print("sending original...")
    special_sendto(client_socket, msg, (IP, PORT))

    # Handle timeouts and receive data from server
    while True:
        client_socket.settimeout(TIMEOUT_IN_SECONDS)
        try:
            server_msg, server_addr = client_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("Timeout exceeded! Retransmitting...")
            special_sendto(client_socket, msg, (IP, PORT))
        else:
            # Get rid of checksum
            server_response = server_msg.decode()[CHECKSUM_LEN:]
            if server_response == "Bad Checksum":
                print("Checksum is bad, retransmitting...")
                continue
            break  # Everything is OK

    print(f"Server sent: {server_response}\n")

client_socket.close()
