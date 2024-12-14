import random
import socket
import threading
import socket_util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UDP_PORT = 12345
TCP_PORT_RANGE = (12400, 12500)
MAX_NUMBER = 100

def create_udp_server(port: int):
    """Create and bind a UDP server socket."""
    try:
        udp_socket = socket_util.create_udp_socket()
        udp_socket.bind(("localhost", port))
        logging.info(f"UDP server created on port {port}")
        return udp_socket
    except Exception as e:
        logging.error(f"Failed to create UDP server: {e}")
        raise

def create_tcp_connection():
    """Create and bind a TCP server socket."""
    try:
        tcp_socket = socket_util.create_tcp_socket()
        tcp_socket.bind(("localhost", random.randint(*TCP_PORT_RANGE)))
        logging.info(f"TCP socket created on port {tcp_socket.getsockname()[1]}")
        return tcp_socket
    except Exception as e:
        logging.error(f"Failed to create TCP connection: {e}")
        raise

def handle_client_guess(conn, game_number):
    """Handle the client's guess and provide feedback."""
    try:
        guess = int(conn.recv(socket_util.get_max_buffer_size()).decode())
        if guess == game_number:
            conn.send(b'CONGRATULATIONS')
            return True
        elif guess < game_number:
            conn.send(b'TRY HIGHER')
        else:
            conn.send(b'TRY LOWER')
        return False
    except ValueError:
        conn.send(b'Invalid input. Please enter a number.')
        return False

def play_game(player_connection, udp_socket):
    """Play the guessing game with the client."""
    try:
        with create_tcp_connection() as tcp_game_socket:
            udp_socket.sendto(str(tcp_game_socket.getsockname()[1]).encode(), player_connection)
            tcp_game_socket.listen(1)
            conn, client_info = tcp_game_socket.accept()
            with conn:
                logging.info(f"New TCP connection from {client_info}")

                game_number = random.randint(0, MAX_NUMBER)
                conn.send(b'WELCOME, pick a number to start')

                while True:
                    if handle_client_guess(conn, game_number):
                        conn.shutdown(socket.SHUT_WR)
                        break

                final_message = conn.recv(socket_util.get_max_buffer_size()).decode()
                logging.info(f"Game ended for {client_info}. Final message: {final_message}")

    except Exception as e:
        logging.error(f"Error in game session: {e}")

if __name__ == '__main__':
    with create_udp_server(UDP_PORT) as udp_socket:
        try:
            while True:
                message, received_from = udp_socket.recvfrom(socket_util.get_max_buffer_size())
                if message == b'START':
                    logging.info(f"New game request from {received_from}")
                    threading.Thread(target=play_game, args=[received_from, udp_socket]).start()
        except KeyboardInterrupt:
            logging.info("Server shutting down.")