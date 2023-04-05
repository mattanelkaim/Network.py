##############################################################################
# server.py
##############################################################################

import socket
import select
import chatlib

users = {}
questions = {}
logged_users = {}  # A dictionary of client hostnames to usernames
client_sockets = []

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5678
BUFFER_SIZE = 1024
ERROR_MSG = "ERROR"


# HELPER SOCKET METHODS

def build_and_send_message(conn: socket, code: str, data: str) -> None:
    """
    Builds a new message using chatlib, using code and message.
    Prints debug info, then sends it to the given socket
    :param conn: The socket connection
    :type conn: socket
    :param code: The command of the message
    :type code: str
    :param data: The data of the message
    :type data: str
    :return: None
    """
    message = chatlib.build_message(code, data)
    print(f"[SERVER] {message}")
    conn.send(message.encode())  # Send to server


def recv_message_and_parse(conn: socket) -> tuple[str, str] | tuple[None, None]:
    """
    Receives a new message from given socket, prints debug info,
    then parses the message using chatlib
    :param conn: The socket connection
    :type conn: socket
    :return: cmd and data of the received message, or (None, None) if error occurred
    :rtype: tuple[str, str] | tuple[None, None]
    """
    full_msg = conn.recv(BUFFER_SIZE).decode()  # Get server response
    print(f"[CLIENT] {full_msg}")
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: questions dictionary
    """
    global questions
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: user dictionary
    """
    global users
    users = {
        "test": {"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }


# SOCKET CREATOR


def setup_socket() -> socket:
    """
    Creates a new listening TCP socket
    :return: The new TCP socket (listening)
    :rtype: socket
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    return server_socket


def send_error(conn: socket, error_msg: str) -> None:
    """
    Send a given error message to the given socket
    :param conn: The socket connection
    :type conn: socket
    :param error_msg: The error info to send back to client
    :type error_msg: str
    :return: None
    """
    build_and_send_message(conn, ERROR_MSG, error_msg)


# MESSAGE HANDLING


def handle_getscore_message(conn: socket, username: str) -> None:
    """
    Gets the score of a given username, then sends it back to client
    :param conn: The socket connection
    :type conn: socket
    :param username: The username whose score needs to be sent
    :type username: str
    :return: None
    """
    global users
    cmd = chatlib.PROTOCOL_SERVER["my_score_ok_msg"]
    data = str(users.get(username)["score"])
    build_and_send_message(conn, cmd, data)


def handle_highscore_message(conn: socket) -> None:
    """
    Finds the top 5 players, then sends them
    back as 'name: score\nname: score...'
    :param conn: The socket connection
    :type conn: socket
    :return: None
    """
    global users
    cmd = chatlib.PROTOCOL_SERVER["highscore_ok_msg"]

    # Get raw data of top 5 users with the highest score
    sorted_users = sorted(users.items(), key=lambda x: x[1]["score"], reverse=True)[:5]
    # Joined with '\n' instead of adding '\n' to every element
    data = "\n".join([f"{name}: {value['score']}" for name, value in sorted_users])

    build_and_send_message(conn, cmd, data)


def handle_logged_message(conn: socket) -> None:
    """
    Sends back all currently logged-in usernames
    :param conn: The socket connection
    :type conn: socket
    :return: None
    """
    global logged_users
    cmd = chatlib.PROTOCOL_SERVER["all_logged_msg"]
    data = ", ".join(logged_users.values())
    build_and_send_message(conn, cmd, data)


def handle_logout_message(conn: socket) -> None:
    """
    Closes the given socket and removes user from logged_users dict
    :param conn: The socket connection
    :type conn: socket
    :return: None
    """
    global logged_users
    global client_sockets

    # Try to get client info
    try:
        client_address = conn.getpeername()
        logged_users.pop(client_address)
    except OSError:
        # The client was forced-closed
        client_address = "unknown"

    client_sockets.remove(conn)
    # TODO REMOVE FROM logged_users IF FORCED-CLOSED
    conn.close()
    print(f"Connection closed for client {client_address}")
    print_clients_sockets(client_sockets)


def handle_login_message(conn: socket, data: str) -> None:
    """
    Validates given login info with users dict. Sends an error to client if needed,
    else sends OK message and adds user and address to logged_users dict
    :param conn: The socket connection
    :type conn: socket
    :param data: The login info to validate
    :type data: str
    :return: None
    """
    global users
    global logged_users
    data = chatlib.split_data(data, 2)
    username, password = data[0], data[1]

    # Validate login info
    if username not in users.keys():
        send_error(conn, "Username does not exist")
        return
    if password != users[username]["password"]:
        send_error(conn, "Password does not match")
        return

    # All ok
    logged_users[conn.getpeername()] = username
    cmd = chatlib.PROTOCOL_SERVER["login_ok_msg"]
    build_and_send_message(conn, cmd, "")


def handle_client_message(conn: socket, cmd: str, data: str) -> None:
    """
    Sends the data to another function based on the command
    :param conn: The socket connection
    :type conn: socket
    :param cmd: The command of the message
    :type cmd: str
    :param data: The data of the message
    :type data: str
    :return: None
    """
    global logged_users

    if conn.getpeername() not in logged_users.keys():
        if cmd == "LOGIN":  # chatlib.PROTOCOL_CLIENT.get("login_msg")
            handle_login_message(conn, data)
        else:
            send_error(conn, "Login first before using this command")
        return

    # User logged-in
    match cmd:
        case "LOGOUT":  # chatlib.PROTOCOL_CLIENT.get("logout_msg")
            handle_logout_message(conn)
        case "MY_SCORE":  # chatlib.PROTOCOL_CLIENT.get("get_score_msg")
            handle_getscore_message(conn, logged_users.get(conn.getpeername()))
        case "HIGHSCORE":  # chatlib.PROTOCOL_CLIENT.get("get_highscore_msg")
            handle_highscore_message(conn)
        case "LOGGED":  # chatlib.PROTOCOL_CLIENT.get("get_logged_msg")
            handle_logged_message(conn)
        # case "PLAY":
        #     play_question(client_socket)
        case _:
            send_error(conn, "Command does not exist")


# SERVER HELPER METHODS


def print_clients_sockets(sockets: list[socket]) -> None:
    """
    Prints all sockets details in a given list of sockets
    :param sockets: The list of the sockets
    :type sockets: list[sockets]
    :return: None
    """
    print("\nConnected clients:")
    if sockets:
        for client in sockets:
            print(f"\t{client.getpeername()}")
    else:
        print("\tNo clients connected!")
    print()  # Newline


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global client_sockets
    load_user_database()
    load_questions()

    server_socket = setup_socket()
    print("Server is up, listening...")

    while True:
        ready_to_read, _, _ = select.select([server_socket] + client_sockets, [], [])

        # Scan the ready-to-read sockets
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                # Add new clients
                client_socket, client_addr = current_socket.accept()
                client_sockets.append(client_socket)
                print_clients_sockets(client_sockets)
            else:
                # Handle clients
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                except (ConnectionResetError, ConnectionAbortedError):
                    handle_logout_message(current_socket)
                    continue

                # Handle client command
                handle_client_message(current_socket, cmd, data)


if __name__ == '__main__':
    main()
