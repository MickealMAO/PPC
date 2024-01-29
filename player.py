import socket
import threading

def receive_messages(sock, message_received_event):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data or data.lower() == 'quit':
                break
            print(f"Received from server: {data}")
            message_received_event.set()  # Signal that a message has been received
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    host = "localhost"
    port = 2050

    # def player_process(host, port):
    message_received_event = threading.Event()

    print('Welcome to the game!')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Connected to the server.")

        thread = threading.Thread(target=receive_messages, args=(client_socket, message_received_event))
        thread.start()

        message = input("Enter message to send: ")
        client_socket.sendall(message.encode())

        while True:
            message_received_event.wait()  # Wait for a message to be received
            message_received_event.clear()  # Clear the event after receiving a message
            message = input("Enter message to send: ")
            if message.lower() == 'quit':
                client_socket.sendall(message.encode())
                break
            client_socket.sendall(message.encode())

        thread.join()





