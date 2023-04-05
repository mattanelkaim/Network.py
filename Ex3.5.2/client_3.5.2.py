"""
Implementing timeouts & retransmissions in a UDP connection
"""
import socket
import random

IP, PORT = "127.0.0.1", 8821
BUFFER_SIZE = 1024
MAX_DIGITS_SERIAL = 4
MAX_SERIAL_NUM = 10_000
TIMEOUT_IN_SECONDS = 5


def special_sendto(conn: socket, response: str, client_address: tuple[str, int]) -> None:
    """
    A sending function provided by the course itself, to simulate packet loss
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


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg, msg_id = "", "0000"
while msg != "EXIT":
    # Get message from user and send to server
    msg = msg_id + input("Enter your message\n")
    print("sending original")
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
            break

    data = server_msg.decode()
    print(f"Server sent: {data}\n")

    # Increment msg_id
    msg_id = str((int(msg_id) + 1) % MAX_SERIAL_NUM).rjust(MAX_DIGITS_SERIAL, "0")

client_socket.close()
