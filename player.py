import socket
import threading

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if data:
                print(f"Received from server: {data}")
            else:
                break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def send_message(sock, message):
    try:
        sock.sendall(message.encode())
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    host = "localhost"
    port = 2050

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Connected to the server.")

        thread = threading.Thread(target=receive_messages, args=(client_socket,))
        thread.start()

        while True:
            message = input("Enter your action: ")
            send_message(client_socket, message)
            if message.lower() == 'quit':
                break

        thread.join()





