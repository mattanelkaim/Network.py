##############################################################################
# server.py
##############################################################################

import socket
import select
import random
import chatlib

users = {}
questions = {}
logged_users = {}  # A dictionary of client hostnames to usernames
client_sockets = []
messages_to_send = []

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5678
BUFFER_SIZE = 1024

USERS_FILE_PATH = r"server database\users.txt"
QUESTIONS_FILE_PATH = r"server database\questions.txt"
ERROR_MSG = "ERROR"
POINTS_PER_QUESTION = 5


# HELPER SOCKET METHODS

def build_and_send_message(conn: socket, code: str, data: str) -> None:
    """
    Builds a new message using chatlib, using code and message.
    Prints debug info, then sends adds message to messages_to_send
    :param conn: The socket connection
    :type conn: socket
    :param code: The command of the message
    :type code: str
    :param data: The data of the message
    :type data: str
    :return: None
    """
    global messages_to_send
    message = chatlib.build_message(code, data)
    print(f"[SERVER] {message}")
    messages_to_send.append((conn, message))


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


def print_client_sockets(sockets: list[socket]) -> None:
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


# DATA LOADERS

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


def load_user_database() -> None:
    """
    Loads users data from a file in this format:
    username|password|score|qID,qID.
    The dictionary's keys are the usernames, their values are
    also dictionaries that contain password, score and questions asked
    :return: None
    """
    global users
    key_names = ("password", "score", "questions_asked")

    with open(USERS_FILE_PATH, 'r') as file:
        content = file.read().splitlines()
        for line in content:
            name, *data = line.split('|')
            data[1] = int(data[1])  # Score
            data[2] = [int(x) for x in data[2].split(',') if bool(x)]  # Questions asked, empty list if empty string
            users[name] = dict(zip(key_names, data))  # Add user data to dictionary


def write_to_users_file() -> None:
    """
    The opposite of load_user_database(): converts
    users info format from a dict to file's format,
    then applies changes to the file
    :return: None
    """
    global users
    content = []

    for user in users.items():
        username, userdata = user[0], list(user[1].values())
        userdata[1] = str(userdata[1])  # Convert score to string
        userdata[2] = map(str, userdata[2])  # Turn to ints to strs
        userdata[2] = ",".join(userdata[2])  # Convert it to 1 string
        content.append('|'.join([username] + userdata))

    with open(USERS_FILE_PATH, 'w') as file:
        file.write('\n'.join(content))


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
    print_client_sockets(client_sockets)


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
    username, password = data

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


def create_random_question() -> str:
    """
    Picks a random question, then returns it
    in the pattern 'id#question#ans1#ans2#...#correct'
    :return: The random question in the protocol format
    :rtype: str
    """
    global questions
    question_id = random.choice(list(questions.keys()))
    question = questions[question_id]
    data = [str(question_id), question["question"], *question["answers"], str(question["correct"])]
    return chatlib.join_data(data)


def handle_question_message(conn: socket) -> None:
    """
    Sends back to client a random question
    :param conn: The socket connection
    :type conn: socket
    :return: None
    """
    cmd = chatlib.PROTOCOL_SERVER["question_ok_msg"]
    data = create_random_question()
    build_and_send_message(conn, cmd, data)


def inc_score(username: str, points: int = POINTS_PER_QUESTION) -> None:
    """
    Increments score for a given username,
    then applies changes to the file database
    :param username: The user to inc their score
    :type username: str
    :param points: Num of points to inc-by (default is POINTS_PER_QUESTION)
    :type points: int
    :return: None
    """
    global users
    users.get(username)["score"] += points
    write_to_users_file()  # Apply changes to database


def handle_answer_message(conn: socket, username: str, data: str) -> None:
    """
    Increments username's score if the answer is right,
    then sends feedback back to the client
    :param conn: The socket connection
    :type conn: socket
    :param username: The username who answered the question
    :type username: str
    :param data: question_id#user_answer
    :type data: str
    :return: None
    """
    global questions
    question_id, answer = chatlib.split_data(data, 2)
    correct_answer = str(questions[int(question_id)]["correct"])

    if answer == correct_answer:
        inc_score(username)
        cmd = chatlib.PROTOCOL_SERVER["correct_answer_msg"]
        data_to_send = ""
    else:
        cmd = chatlib.PROTOCOL_SERVER["wrong_answer_msg"]
        data_to_send = correct_answer

    build_and_send_message(conn, cmd, data_to_send)


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
        case "GET_QUESTION":  # chatlib.PROTOCOL_CLIENT.get("get_question_msg")
            handle_question_message(conn)
        case "SEND_ANSWER":  # chatlib.PROTOCOL_CLIENT.get("send_answer_msg")
            handle_answer_message(conn, logged_users.get(conn.getpeername()), data)
        case _:
            send_error(conn, "Command does not exist")


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global client_sockets
    global messages_to_send
    load_user_database()
    load_questions()

    server_socket = setup_socket()
    print(f"Server is up and listening on port {SERVER_PORT}...")

    while True:
        ready_to_read, ready_to_write, _ = select.select([server_socket] + client_sockets, client_sockets, [])

        # Scan the ready-to-read sockets
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                # Add new clients
                client_socket, client_addr = current_socket.accept()
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                # Handle clients
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                except (ConnectionResetError, ConnectionAbortedError):
                    handle_logout_message(current_socket)
                    continue

                # Handle client command
                handle_client_message(current_socket, cmd, data)

        # Send all messages
        for msg in messages_to_send:
            conn, data = msg
            if conn in ready_to_write:
                conn.send(data.encode())  # Send to client
                messages_to_send.remove(msg)


if __name__ == '__main__':
    main()
