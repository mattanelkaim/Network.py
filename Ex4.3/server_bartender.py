"""
A TCP echo server that can handle multiple TCP sockets
"""
import socket
import select

IP, PORT = "0.0.0.0", 5555
BUFFER_SIZE = 1024


def print_clients_sockets(sockets: list[socket.socket]) -> None:
    """
    Prints all sockets details in a given list of sockets
    :param sockets: The list of the sockets
    :return: None
    """
    print("\nConnected clients:")
    if sockets:
        for client in sockets:
            print(f"\t{client.getpeername()}")
    else:
        print("\tNo clients connected!")
    print()  # Newline


def close_socket(conn: socket.socket, client_sockets: list[socket.socket]) -> None:
    """
    Closes a client socket and removes it from the list,
    then prints connected clients
    :param conn: The socket connection to close
    :param client_sockets: The list of all client sockets
    :return: None
    """
    try:
        client_address = conn.getpeername()
    except OSError:
        # The client was forced-closed
        client_address = "unknown"
    client_sockets.remove(conn)
    conn.close()
    print(f"Connection closed for client {client_address}")
    print_clients_sockets(client_sockets)


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Server is up, listening...")

    client_sockets = []
    unsent_messages = []  # In case client isn't ready to receive messages
    while True:
        ready_to_read, ready_to_write, _ = select.select(
            [server_socket] + client_sockets, client_sockets, [])

        # Scan the ready-to-read sockets
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                # Add new clients
                client_socket, _ = current_socket.accept()
                client_sockets.append(client_socket)
                print_clients_sockets(client_sockets)
            else:
                # Handle clients
                try:
                    data = current_socket.recv(BUFFER_SIZE).decode()
                except (ConnectionResetError, ConnectionAbortedError):
                    close_socket(current_socket, client_sockets)
                    continue

                if not bool(data):  # More optimized than data == ""
                    # Client wants to disconnect
                    close_socket(current_socket, client_sockets)
                else:
                    # Handle echo back to client
                    print(f"{current_socket.getpeername()} sent: {data}")
                    if current_socket in ready_to_write:
                        current_socket.send(data.encode())
                    else:
                        # Send it in future iterations
                        unsent_messages.append((current_socket, data))

        # Send messages if client isn't occupied
        for msg in unsent_messages:
            current_socket, data = msg
            if current_socket in ready_to_write:
                current_socket.send(data.encode())
                unsent_messages.remove(msg)


if __name__ == '__main__':
    main()
