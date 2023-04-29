"""
The interactive server of the trivia game, protocol in network.py course
"""
import logging
import socket
import select
import random
import hashlib  # To create unique question IDs
import json
import html  # To remove HTML codes
import requests
import chatlib

users = {}
questions = {}
logged_users = {}  # Tuples of sockets and usernames
client_sockets = set()
messages_to_send = []

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5678
BUFFER_SIZE = 1024

USERS_FILE_PATH = r"server database\users.json"
QUESTIONS_FILE_PATH = r"server database\questions.json"
QUESTIONS_API_URL = "https://opentdb.com/api.php"
# Category 18 is computer science
QUESTIONS_SETTINGS = {"amount": "50", "type": "multiple", "category": "18"}
ERROR_MSG = "ERROR"
POINTS_PER_QUESTION = 5


# HELPER SOCKET METHODS

def build_and_send_message(conn: socket, code: str, data: str) -> None:
    """
    Builds a new message using chatlib format, using code and data.
    Logs debug info, then appends msg to messages_to_send
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
    logging.debug(f"[SERVER] {message}")
    messages_to_send.append((conn, message))


def recv_msg_and_parse(conn: socket) -> tuple[str, str] | tuple[None, None]:
    """
    Receives a new message from given socket, logs debug info,
    then parses the message using chatlib format
    :param conn: The socket connection
    :type conn: socket
    :return: cmd and data of received message, (None, None) if error occurred
    :rtype: tuple[str, str] | tuple[None, None]
    """
    full_msg = conn.recv(BUFFER_SIZE).decode()  # Get server response
    logging.debug(f"[CLIENT] {full_msg}")
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


def print_client_sockets(sockets: set[socket]) -> None:
    """
    Logs all sockets details in a given list of sockets
    :param sockets: The list of the sockets
    :type sockets: set[sockets]
    :return: None
    """
    # Get clients' IPs and ports
    connected_clients = []
    for client in sockets:
        client_address = client.getpeername()  # Compute only once
        connected_clients.append(f"{client_address[0]}:{client_address[1]}")

    # Log the details
    if connected_clients:
        connected_clients = '\n\t'.join(connected_clients)
        message = f"Connected clients:\n\t{connected_clients}"
    else:
        message = "No connected clients"
    logging.info(message)


# DATA LOADERS

def load_questions() -> None:
    """
    Loads questions dict from a JSON file.
    The dictionary's keys are the question IDs, their values are
    sub-dicts that contain question, 4 answers and correct answer.
    :return: None
    """
    global questions
    with open(QUESTIONS_FILE_PATH, 'r') as file:
        questions = json.load(file)


def load_questions_from_web() -> None:
    """
    Gets questions from a web service, removes ones that contain
    the DATA_DELIMITER (HTML codes excluded), then append a unique
    ID for each question using hashing, create a dictionary of all
    questions and save them to a JSON file
    :return: None
    """
    global questions

    stock = requests.get(QUESTIONS_API_URL, params=QUESTIONS_SETTINGS).json().get("results")
    data_delimiter = chatlib.DATA_DELIMITER

    # Remove invalid questions & append unique IDs for each question
    for question in stock:
        # Data might be with HTML codes, remove these
        question["question"] = html.unescape(question["question"])
        question["correct_answer"] = html.unescape(question["correct_answer"])
        question["incorrect_answers"] = [html.unescape(answer) for answer in question["incorrect_answers"]]

        # if char '#' is still in question data, ignore question
        if data_delimiter in question["question"]\
                or data_delimiter in question["correct_answer"]\
                or any(data_delimiter in ans for ans in question["incorrect_answers"]):
            continue

        # Hash the question to get a unique ID (hash-collision changes are low)
        question_id = hashlib.md5(question["question"].encode()).hexdigest()[:8]
        questions[question_id] = question  # Add question to dictionary

    # Save changes to a file
    with open(r"server database\web_questions.json", 'w') as file:
        json.dump(questions, file, indent=4)

    logging.info("Requested new questions successfully")


def load_user_database() -> None:
    """
    Loads users dict from a JSON file.
    The dictionary's keys are the usernames, their values are
    sub-dicts that contain password, score and questions asked.
    :return: None
    """
    global users
    with open(USERS_FILE_PATH, 'r') as file:
        users = json.load(file)


def write_to_users_file() -> None:
    """
    The opposite of load_user_database():
    writes users dict to a JSON file
    :return: None
    """
    global users
    with open(USERS_FILE_PATH, 'w') as file:
        json.dump(users, file, indent=4)


# MESSAGE HANDLING

def handle_get_score_message(conn: socket, username: str) -> None:
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
    except (OSError, KeyError):
        # The client was forced-closed
        client_address = "unknown"

    client_sockets.remove(conn)
    conn.close()
    logging.debug(f"Connection closed for client {client_address}")
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


def create_random_question(username: str) -> str | None:
    """
    Picks a random question, then returns it
    in the format 'id#question#ans1#ans2#...#correct'
    :return: The random question in the protocol format, None if no questions left
    :rtype: str | None
    """
    global questions
    global users

    # Get questions' IDs that were not asked
    questions_asked = set(users[username]["questions_asked"])
    questions_not_asked = set(questions.keys()).difference(questions_asked)
    if not questions_not_asked:
        # All questions were asked
        return None

    # Pick a question & convert to protocol's format
    question_id = random.sample(list(questions_not_asked), k=1)[0]  # Get a random ID
    question_data = questions[question_id]
    actual_question = html.unescape(question_data["question"])  # Data might be with HTML codes, remove these
    answers = [question_data["correct_answer"]] + question_data["incorrect_answers"]  # 1 list of all possible answers
    random.shuffle(answers)  # Randomize order of answers
    data = [str(question_id), actual_question, *answers]
    return chatlib.join_data(data)


def handle_question_message(conn: socket) -> None:
    """
    Sends back to client a random question
    :param conn: The socket connection
    :type conn: socket
    :return: None
    """
    global logged_users
    username = logged_users.get(conn.getpeername())

    # Get a random question
    question = create_random_question(username)
    if question is None:
        # No questions left
        cmd = chatlib.PROTOCOL_SERVER["no_questions_msg"]
        data = ""
    else:
        # Send question to client
        cmd = chatlib.PROTOCOL_SERVER["question_ok_msg"]
        data = question

    build_and_send_message(conn, cmd, data)


def inc_score(username: str, points: int = POINTS_PER_QUESTION) -> None:
    """
    Increments score for a given username
    :param username: The user to inc their score
    :type username: str
    :param points: Num of points to inc-by (default is POINTS_PER_QUESTION)
    :type points: int
    :return: None
    """
    global users
    users.get(username)["score"] += points
    # Write changes to database later in handle_answer_message()


def handle_answer_message(conn: socket, username: str, data: str) -> None:
    """
    Increments username's score if the answer is right,
    adds qID to questions asked,
    then applies changes to file database and
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
    global users
    question_id, answer = chatlib.split_data(data, 2)
    correct_answer = questions[question_id]["correct_answer"]

    # Add qID to questions asked
    users[username]["questions_asked"].append(question_id)

    # Handle & check answer
    if answer == correct_answer:
        inc_score(username)
        cmd = chatlib.PROTOCOL_SERVER["correct_answer_msg"]
        data_to_send = ""
    else:
        cmd = chatlib.PROTOCOL_SERVER["wrong_answer_msg"]
        data_to_send = correct_answer

    write_to_users_file()  # Apply questions_asked and score inc to database
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
            handle_get_score_message(conn, logged_users.get(conn.getpeername()))
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
    global users
    global questions
    global client_sockets
    global messages_to_send

    # Config logging for info & debug
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

    # Load data
    load_user_database()
    # load_questions()  # From a static file
    load_questions_from_web()

    server_socket = setup_socket()
    logging.info(f"Server is up and listening on port {SERVER_PORT}...")

    while True:
        # Scan new data from all sockets into lists
        ready_to_read, ready_to_write, _ = select.select({server_socket}.union(client_sockets), client_sockets, [])

        # Scan the ready-to-read sockets
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                # Add new clients
                client_socket, client_addr = current_socket.accept()
                client_sockets.add(client_socket)
                print_client_sockets(client_sockets)
            else:
                # Handle clients
                try:
                    cmd, data = recv_msg_and_parse(current_socket)
                except (ConnectionResetError, ConnectionAbortedError):
                    handle_logout_message(current_socket)
                    continue

                if not bool(cmd):
                    # Empty string, user wants to disconnect
                    handle_logout_message(current_socket)
                else:
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
