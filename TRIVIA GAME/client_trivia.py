import socket
import chatlib

SERVER_IP = "loopback"  # CHANGE TO SERVER'S IP
SERVER_PORT = 5678
BUFFER_SIZE = 1024
IS_DEBUG = False  # Print debug info in functions


def build_and_send_message(conn: socket.socket, code: str, data: str) -> None:
    """
    Builds a new message using chatlib, using code and message.
    Prints debug info, then sends it to the given socket
    :param conn: The socket connection
    :param code: The command of the message
    :param data: The data of the message
    """
    message = chatlib.build_message(code, data)

    if IS_DEBUG:
        print(f"Sending:  {message}")
    conn.send(message.encode())  # Send to server


def recv_msg_and_parse(conn: socket.socket) -> tuple[str, str] | tuple[None, None]:
    """
    Receives a new message from given socket, prints debug info,
    then parses the message using chatlib
    :param conn: The socket connection
    :return: cmd and data of received message, (None, None) if error occurred
    """
    full_msg = conn.recv(BUFFER_SIZE).decode()  # Get server response

    if IS_DEBUG:
        print(f"Received: {full_msg}")
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def build_send_recv_parse(conn: socket.socket, cmd: str, data: str) -> tuple[str, str] | tuple[None, None]:
    """
    Joins the sending & receiving functions to 1
    :param conn: The socket connection
    :param cmd: The command of the message
    :param data: The data of the message
    :return: cmd and data of the response, or (None, None) if error occurred
    """
    build_and_send_message(conn, cmd, data)
    cmd, data = recv_msg_and_parse(conn)
    return cmd, data


def error_and_exit(error_msg: str) -> None:
    """
    Prints an error and terminates the program
    :param error_msg: The error to print
    :return: None
    """
    print(error_msg)
    exit()  # Terminate program


def login(conn: socket.socket) -> None:
    """
    Uses user's input to send to socket login info,
    then loops until login is successful
    :param conn: The socket connection
    :return: None
    """
    while True:
        # Get user input
        try:
            username = input("Enter username:\n")
            password = input("Enter password:\n")
        except KeyboardInterrupt:
            error_and_exit("Goodbye!")
            return

        # Check validity
        if chatlib.DELIMITER in username or chatlib.DATA_DELIMITER in username:
            print("Username can't contain | nor #. Please try again:")
            continue
        if chatlib.DELIMITER in password or chatlib.DATA_DELIMITER in password:
            print("Password can't contain | nor #. Please try again:")
            continue
        user_info = chatlib.join_data([username, password])

        # Send to server & get response
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], user_info)
        response_cmd, response_data = recv_msg_and_parse(conn)

        # Check if login was successful
        if response_cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            print("Login successful!")
            return
        else:
            print(f"{response_data}. Please try again:\n")


def logout(conn: socket.socket) -> None:
    """
    Sends to the server a logout request, prints debug info
    :param conn: The socket connection
    :return: None
    """
    cmd = chatlib.PROTOCOL_CLIENT["logout_msg"]
    build_and_send_message(conn, cmd, "")
    print("Logout successful!")


def get_score(conn: socket.socket) -> None:
    """
    Prints current score of user
    :param conn: The socket connection
    :return: None
    """
    # Send a request to server and get cmd & data
    cmd = chatlib.PROTOCOL_CLIENT["get_score_msg"]
    cmd, data = build_send_recv_parse(conn, cmd, "")

    if cmd != chatlib.PROTOCOL_SERVER["my_score_ok_msg"]:
        error_and_exit(data)  # data holds error info

    print(f"Your score is {data}")


def get_highscore(conn: socket.socket) -> None:
    """
    Prints the highscore table
    :param conn: The socket connection
    :return: None
    """
    # Send a request to server and get cmd & data
    cmd = chatlib.PROTOCOL_CLIENT["get_highscore_msg"]
    cmd, data = build_send_recv_parse(conn, cmd, "")

    if cmd != chatlib.PROTOCOL_SERVER["highscore_ok_msg"]:
        error_and_exit(data)  # data holds error info

    print(f"High-score table:\n{data}")


def get_logged_users(conn: socket.socket) -> None:
    """
    Prints all users that are logged-in to the server
    :param conn: The socket connection
    :return: None
    """
    cmd = chatlib.PROTOCOL_CLIENT["get_logged_msg"]
    cmd, data = build_send_recv_parse(conn, cmd, "")

    if cmd == chatlib.PROTOCOL_SERVER["all_logged_msg"]:
        print(f"Logged users:\n{data}")
    else:
        error_and_exit(data)  # data holds error info


def play_question(conn: socket.socket) -> None:
    """
    Asks server for a question, sends the server the user's
    answer and displays the feedback from the server
    :param conn: The socket connection
    :return: None
    """
    # Get question from server
    cmd = chatlib.PROTOCOL_CLIENT["get_question_msg"]
    cmd, data = build_send_recv_parse(conn, cmd, "")

    # Handle edge-case
    if cmd == chatlib.PROTOCOL_SERVER["no_questions_msg"]:
        print("You are so smart... or not. No questions left!")
        return

    # Build question and answers for display
    data = chatlib.split_data(data, 6)
    question_id, question, *answers = data
    print(f"Question: {question}")
    # Print answers
    for index, val in enumerate(answers, 1):
        print(f"\t{index}: {val}")

    # Get a valid answer from user and send to server
    while True:
        try:
            answer = input("Enter the answer (1-4): ")
        except KeyboardInterrupt:
            error_and_exit("Goodbye!")
            return

        if answer in {"1", "2", "3", "4"}:
            break
        else:
            print("Invalid answer!")

    formatted_answer = chatlib.join_data([question_id, answers[int(answer) - 1]])  # Get index
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer_msg"], formatted_answer)

    # Show feedback to user
    if cmd == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
        print(f"Wrong! The answer was {data}")
    elif cmd == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
        print("U R RIGHT!!!")
    else:  # Error
        error_and_exit(data)


def print_menu() -> None:
    """
    Lists all commands and their functionalities
    :return: None
    """
    print("All commands:\n"
          "LOGOUT ------- logs out the user\n"
          "MENU --------- lists all commands\n"
          "SCORE -------- prints current score of user\n"
          "HIGHSCORE ---- prints a table of high scores\n"
          "LOGGED ------- prints all connected users\n"
          "PLAY --------- get a question and choose the answer")


def main():
    # Establish connection with server
    client_socket = socket.create_connection((SERVER_IP, SERVER_PORT))
    login(client_socket)

    print()  # Newline
    print_menu()
    while True:
        print()  # Newline
        try:
            operation = input("Type command here...\n").upper()
        except KeyboardInterrupt:
            error_and_exit("Goodbye!")
            return

        match operation:
            case "LOGOUT":
                break
            case "MENU":
                print_menu()
            case "SCORE":
                get_score(client_socket)
            case "HIGHSCORE":
                get_highscore(client_socket)
            case "LOGGED":
                get_logged_users(client_socket)
            case "PLAY":
                play_question(client_socket)
            case _:
                print("No such command!")

    # End game
    logout(client_socket)
    client_socket.close()


if __name__ == '__main__':
    main()
