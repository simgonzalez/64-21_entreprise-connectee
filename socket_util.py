import socket


def get_max_buffer_size():
    return 4096

def create_tcp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def create_udp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
