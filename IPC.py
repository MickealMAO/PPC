import socket
import signal
from multiprocessing import Queue

def create_server_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    return server_socket

def accept_client_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    return client_socket, client_address

def send_data(client_socket, data):
    client_socket.sendall(data)

def receive_data(client_socket):
    return client_socket.recv(1024)  # 假设数据不会超过 1024 字节

def create_message_queue():
    return Queue()

# 设置信号处理器
def setup_signal_handler(signal_number, handler_function):
    signal.signal(signal_number, handler_function)