import socket_util
import sys

SERVER_IP = "localhost"
SERVER_UDP_PORT = 12345

def initiate_udp_connection():
    """Initiate a UDP connection to the server and get the TCP port."""
    try:
        with socket_util.create_udp_socket() as udp_socket:
            udp_socket.sendto(b'START', (SERVER_IP, SERVER_UDP_PORT))
            tcp_port_data, _ = udp_socket.recvfrom(socket_util.get_max_buffer_size())
            return int(tcp_port_data.decode())
    except Exception as e:
        print(f"Error in UDP connection: {e}")
        sys.exit(1)

def establish_tcp_connection(tcp_port):
    """Establish a TCP connection to the server using the provided port."""
    tcp_socket = socket_util.create_tcp_socket()
    try:
        tcp_socket.connect((SERVER_IP, tcp_port))
        welcome_message = tcp_socket.recv(socket_util.get_max_buffer_size()).decode()
        print(welcome_message)
        return tcp_socket
    except Exception as e:
        print(f"Error in TCP connection: {e}")
        sys.exit(1)

def play_game(tcp_socket):
    """Play the guessing game with the server."""
    while True:
        guess = input("Enter your guess: ")
        tcp_socket.send(guess.encode())
        response = tcp_socket.recv(socket_util.get_max_buffer_size()).decode()
        print(response)
        if response == 'CONGRATULATIONS':
            tcp_socket.send(b'THANKS')
            break

if __name__ == '__main__':
    tcp_port = initiate_udp_connection()
    tcp_socket = establish_tcp_connection(tcp_port)

    try:
        play_game(tcp_socket)
    except Exception as e:
        print(f"Error during game: {e}")
    finally:
        tcp_socket.close()