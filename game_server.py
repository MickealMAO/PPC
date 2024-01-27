import socket
import concurrent.futures
import select

HOST = "localhost"
PORT = 1789

def socket_handler(client_socket, address):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response = "Your response here"
            client_socket.sendall(response.encode())
    finally:
        client_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setblocking(False)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        connections = []
        while True:
            readable, _, _ = select.select([server_socket] + connections, [], [])
            for s in readable:
                if s is server_socket:
                    client_socket, address = server_socket.accept()
                    client_socket.setblocking(False)
                    connections.append(client_socket)
                else:
                    executor.submit(socket_handler, s, address)
import socket
import concurrent.futures
import select

HOST = "localhost"
PORT = 1789

def socket_handler(client_socket, address):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response = "Your response here"
            client_socket.sendall(response.encode())
    finally:
        client_socket.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setblocking(False)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        connections = []
        while True:
            readable, _, _ = select.select([server_socket] + connections, [], [])
            for s in readable:
                if s is server_socket:
                    client_socket, address = server_socket.accept()
                    client_socket.setblocking(False)
                    connections.append(client_socket)
                else:
                    executor.submit(socket_handler, s, address)
