import pickle
import socket
from _thread import *
import sys
import signal
from player import Player

server = ""  # Adjust for your local network IP
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(f"Bind failed: {e}")
    sys.exit(1)

s.listen(4)  # Max clients
print("Server started. Waiting for connections...")

running = True  # Flag to control the main loop


# For shutting down the server
def signal_handler(sig, frame):
    global running
    print("\nCtrl+C detected. Shutting down server...")
    running = False
    s.close()  # Close the socket
    sys.exit(0)  # Exit the program


signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler


players = [Player(0, 0, 50, 50, (255, 0, 0)), Player(0, 0, 50, 50, (0, 255, 0))]


def threaded_client(conn, player):
    """Handles communication with a single client."""
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            # Receive the data from the client and parse the position
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            if not data:
                print(f"Player {player} disconnected")
                break

            if player == 1:
                reply = players[0]
            else:
                reply = players[1]

            print(f"Received: {data} from player {player}")
            print(f"Sending: {reply} to player {player}")
            conn.sendall(pickle.dumps(reply))  # Send the position of the other player

        except Exception as e:
            print(f"Error with player {player}: {e}")
            break
    print(f"Connection with player {player} lost")
    conn.close()


currentPlayer = 0
while running:
    try:
        conn, addr = s.accept()
        print(f"Player {currentPlayer + 1} connected: {addr}")

        # If the server already has 2 players, refuse the new connection
        if currentPlayer >= 2:
            conn.sendall(str.encode("Server full, try again later."))
            print(f"Refusing connection from {addr}, server full")
            conn.close()  # Reject the connection
            continue  # Continue the loop to check for other connections

        # Start a new thread for the connected player
        start_new_thread(threaded_client, (conn, currentPlayer))
        currentPlayer += 1  # Increase player count for each connection

    except (OSError, Exception) as e:
        if not running:
            break
        else:
            print(f"Error accepting connection: {e}")

print("Server stopped.")
