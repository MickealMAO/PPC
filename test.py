import socket
import threading
import multiprocessing
import queue as QueueModule
import time

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            print(f"Received from server: {data}")
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def player_process(host, port, queue):
    print('Welcome to the game!')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Connected to the server.")

        # Create a thread to handle incoming messages from the server
        thread = threading.Thread(target=receive_messages, args=(client_socket,))
        thread.start()

        while True:
            try:
                message = queue.get_nowait()
                if message == 'quit':
                    client_socket.sendall(message.encode())
                    break
                client_socket.sendall(message.encode())
            except QueueModule.Empty:
                time.sleep(0.1)  # Short delay to prevent busy waiting
                continue

        thread.join()

if __name__ == "__main__":
    host = "localhost"
    port = 2050
    message_queue = multiprocessing.Queue()
    player_proc = multiprocessing.Process(target=player_process, args=(host, port, message_queue))
    player_proc.start()

    while True:
        message = input("Enter message to send: ")
        message_queue.put(message)
        if message == "quit":
            break

    player_proc.join()
