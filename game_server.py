import socket
import concurrent.futures
import select
import errno
import multiprocessing

def socket_handler(player_socket, address, active_players):
    """Handle the socket connection for each player."""
    try:
        while True:
            try:
                data = player_socket.recv(1024)
                if not data:
                    print(f"Client {address} disconnected")
                    break
                print(f"Received from client: {data.decode()}")
                response = "Server received: " + data.decode()
                player_socket.sendall(response.encode())
            except socket.error as e:
                if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                    continue
                else:
                    raise e
    except Exception as e:
        print(f"Error in handling player socket: {e}")
    finally:
        player_socket.close()
        active_players.remove(player_socket)

def server_process(host, port):
    """Run the server process."""
    active_players = []

    print("Starting server...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setblocking(False)
        server_socket.bind((host, port))
        server_socket.listen(4)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            while True:
                readable, _, _ = select.select([server_socket] + active_players, [], [])
                for s in readable:
                    if s is server_socket:
                        player_socket, address = server_socket.accept()
                        player_socket.setblocking(False)
                        active_players.append(player_socket)
                        executor.submit(socket_handler, player_socket, address, active_players)
                    else:
                        executor.submit(socket_handler, s, address, active_players)

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 2050

    server_proc = multiprocessing.Process(target=server_process, args=(HOST, PORT))
    server_proc.start()
    server_proc.join() 


