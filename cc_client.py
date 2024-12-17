import socket
import threading
from time import sleep

import socket_util
import sys
import random
import logging

SERVER_IP = "localhost"
SERVER_UDP_PORT = 12345
TCP_PORT_RANGE = (12400, 12500)
MAX_NUMBER = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initiate_udp_connection():
    """Initiate a UDP connection to the server and get the TCP port."""
    try:
        udp_socket = socket_util.create_udp_socket()
        udp_socket.sendto(b'START', (SERVER_IP, SERVER_UDP_PORT))
        return udp_socket
    except Exception as e:
        logging.error(f"Error in UDP connection: {e}")
        sys.exit(1)

def create_tcp_server():
    """Create and bind a TCP server socket."""
    try:
        tcp_socket = socket_util.create_tcp_socket()
        tcp_socket.bind(("localhost", random.randint(*TCP_PORT_RANGE)))
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

def play_game_client(conn):
    """Play the guessing game with the server."""
    print(conn.recv(socket_util.get_max_buffer_size()).decode()) #Welcome message
    while True:
        guess = input("Enter your guess: ")
        conn.send(guess.encode())
        response = conn.recv(socket_util.get_max_buffer_size()).decode()
        print(response)
        if response == 'CONGRATULATIONS':
            break

def play_game_server(tcp_conn):
    """Play the guessing game with the client."""
    try:
        count_tries = 0
        game_number = random.randint(0, MAX_NUMBER)
        tcp_conn.send(b'WELCOME, pick a number to start')

        while True:
            count_tries += 1
            if handle_client_guess(tcp_conn, game_number):
                break
        return count_tries
    except Exception as e:
        logging.error(f"Error in game session: {e}")

def send_score(tries, udp_socket):
    udp_socket.sendto(f"SCORE {tries}".encode(), (SERVER_IP, SERVER_UDP_PORT))

def main():
    with initiate_udp_connection() as udp_socket:
        client_state = udp_socket.recv(socket_util.get_max_buffer_size()).decode()
        tries = 0
        if client_state == "WAIT":
            with create_tcp_server() as tcp_game_socket:
                udp_socket.sendto(str(tcp_game_socket.getsockname()[1]).encode(), (SERVER_IP, SERVER_UDP_PORT))
                tcp_game_socket.listen(1)
                conn, client_info = tcp_game_socket.accept()

                tries = play_game_server(conn)
                play_game_client(conn)
                conn.close()
        elif "PEER" in client_state:
            with socket_util.create_tcp_socket() as tcp_socket:
                peer_info = client_state.split(" ")
                tcp_socket.connect((peer_info[1], int(peer_info[2])))

                play_game_client(tcp_socket)
                tries = play_game_server(tcp_socket)
                tcp_socket.close()
        send_score(tries, udp_socket)

if __name__ == '__main__':
    threading.Thread(target=main).start()
