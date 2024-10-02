import random
import socket
import threading

from models import Settings
from models.Player import Player


class NetCodeServer:
    def __init__(self):
        self.clients = []
        threading.Thread(target=self.server_thread, daemon=True).start()

    def handle_client(self, conn, addr):
        print(f'Connected by {addr}')

        # Add this client to the list of connected clients
        self.clients.append(conn)

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f'Client {addr} disconnected.')
                    break

                if data.decode() == 'spawn':
                    # Generate random spawn coordinates
                    x = random.randint(400, 600)
                    y = random.randint(400, 600)
                    spawn_location = f'{x},{y}'
                    print(f'Player from {addr} spawned at {spawn_location}')

                    # Broadcast the new spawn location to all clients
                    self.broadcast(f'spawn:{spawn_location}')

        except ConnectionResetError:
            print(f'Connection with {addr} reset.')
        finally:
            # Remove the client from the list when the connection is closed
            self.clients.remove(conn)
            conn.close()

    # Function to broadcast a message to all clients except the one that triggered the event
    def broadcast(self, message, sender_conn=None):
        for client in self.clients:
            if client != sender_conn:  # Don't send the message back to the original client
                try:
                    client.sendall(message.encode())
                except Exception as e:
                    print(f'Error sending to client: {e}')

    def server_thread(self):
        host = '127.0.0.1'
        port = 8888

        # Create a socket object and bind it to the host and port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()

            print(f'Server running on {host}:{port}')
            while True:
                conn, addr = s.accept()
                # Start a new thread to handle the client with a persistent connection
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()


class NetCodeClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.server = self.setup_connection()
        threading.Thread(target=self.listen_to_server, args=(self.server,), daemon=True).start()
        self.server.sendall(b'spawn')

    # Function to handle communication with the server in a separate thread
    def listen_to_server(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    message = data.decode()
                    if message.startswith('spawn:'):
                        # This message is the player's own spawn location
                        spawn_location = message.split(":")[1]
                        x, y = map(int, spawn_location.split(","))
                        Player((x, y), self.settings)
            except Exception as e:
                print(f'Error receiving data from server: {e}')
                break

    # Function to set up persistent connection to the server
    def setup_connection(self):
        host = '127.0.0.1'
        port = 8888
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))
        print(f'Connected to server at {host}:{port}')
        return server
