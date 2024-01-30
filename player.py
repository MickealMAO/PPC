import socket
import threading

def receive_messages(sock):
    """receive and print messages from the server"""
    while True:
        try:
            data = sock.recv(1024).decode()
            if data:
                print(f"{data}")
            else:
                break  
        except Exception as e:
            print(f"Error receiving data: {e}")
            break  

def send_message(sock, message):
    """send messages to the server"""
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

        # create a thread to receive messages from the server
        thread = threading.Thread(target=receive_messages, args=(client_socket,))
        thread.start()

        while True:
            message = input("Say something to the server: ")
            send_message(client_socket, message)
            if message.lower() == 'quit':
                break  # 如果输入 'quit'，退出循环
            pass

        thread.join() 





