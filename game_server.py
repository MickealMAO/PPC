import socket
import concurrent.futures
import select

# Server host and port configuration
HOST = "localhost"
PORT = 1789

# Function to handle each player's socket connection
def socket_handler(player_socket, address):
    try:
        while True:
            # Receiving data from client
            data = player_socket.recv(1024)
            if not data:
                break  # Exit loop if no data received
            response = "Your response here" 
            player_socket.sendall(response.encode())  # Sending response back to client
    finally:
        player_socket.close()  # Ensure the socket is closed eventually

# Creating a TCP socket for the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setblocking(False)  # Set the socket to non-blocking mode
    server_socket.bind((HOST, PORT))  
    server_socket.listen(4) 

    # Creating a thread pool with 4 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        active_players = []  # Store active player connections
        while True:
            # Using select to check for ready-to-read sockets
            readable, _, _ = select.select([server_socket] + active_players, [], [])
            for s in readable:
                if s is server_socket:
                    # Accepting new connection if server socket is ready to read
                    player_socket, address = server_socket.accept()
                    player_socket.setblocking(False)  
                    active_players.append(player_socket)  # Add new player to the active players list
                else:
                    # Submitting player socket handler function to the thread pool
                    executor.submit(socket_handler, s, address)

