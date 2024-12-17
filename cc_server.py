import random
import socket
import threading
import socket_util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UDP_PORT = 12345
TCP_PORT_RANGE = (12400, 12500)

games = []


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

if __name__ == '__main__':
    try:
        client_waiter = ();
        with create_udp_server(UDP_PORT) as udp_socket:
            while True:
                message, received_from = udp_socket.recvfrom(socket_util.get_max_buffer_size())
                if message == b'START':
                    logging.info(f"New game request from {received_from}")
                    # if the player is second to arrive we go here
                    if client_waiter != ():
                        udp_socket.sendto(f"PEER {client_waiter[0]} {client_waiter[1]}".encode(), received_from)
                        games.append({client_waiter: 0, received_from: 0})
                        client_waiter = ()
                    # if the player is first to arrive it creates the lobby
                    else:
                        logging.info("No client in matchmaking")
                        udp_socket.sendto(b'WAIT', received_from)
                        logging.info("Waiting to receive port number from client")
                        port_as_string = udp_socket.recv(socket_util.get_max_buffer_size()).decode()
                        try:
                            port = int(port_as_string)
                            if port < TCP_PORT_RANGE[0] or port > TCP_PORT_RANGE[1]:
                                raise ValueError
                            client_waiter = (received_from[0], port)
                            logging.info(f"Port from client received {port}")
                        except ValueError:
                            logging.error("Invalid port number received")
                            continue
                elif "SCORE" in message.decode(): # the messages might not be processed quickly enough and my client might be sending it at the same time which sucks
                    print (received_from[0]+ ":" + str(received_from[1]) + " "+message.decode()) # TODO make fstring
                    # this code is supposed to retrieve the game to show it properly i couldn't make it work so
                    # for game in games:
                    #     if received_from in game.keys():
                    #         game[received_from] = int(message.decode().split(" ")[1])
                    #         break
                    #     if all(val > 0 for val in game.values()):
                    #         logging.info(f"GAME FINISHED {game}")

    except KeyboardInterrupt:
        logging.info("Server shutting down.")
