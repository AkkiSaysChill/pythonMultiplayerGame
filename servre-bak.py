# Server-side threading for handling multiple clients
import socket
from _thread import *
import sys
import signal
from threading import Lock

server = "192.168.31.166"  # Adjust for your local network IP
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


def read_pos(str):
    """Reads position data from a string and returns it as a tuple (x, y)."""
    str = str.split(",")
    return int(str[0]), int(str[1])


def make_pos(tup):
    """Converts a tuple (x, y) to a string."""
    return f"{tup[0]},{tup[1]}"


# Starting positions for the players
pos = [(400, 400), (100, 100)]  # Default positions
pos_lock = Lock()


def threaded_client(conn, player):
    """Handles communication with a single client."""
    conn.send(str.encode(make_pos(pos[player])))  # Send starting position to the client
    reply = ""
    while True:
        try:
            # Receive the data from the client and parse the position
            data = conn.recv(2048).decode()
            if not data:
                print(f"Player {player} disconnected")
                break

            data = read_pos(data)

            # Update the player's position
            with pos_lock:
                pos[player] = data

            # Send the other player's position
            if player == 1:
                reply = pos[0]
            else:
                reply = pos[1]

            print(f"Received: {data} from player {player}")
            print(f"Sending: {reply} to player {player}")
            conn.sendall(
                str.encode(make_pos(reply))
            )  # Send the position of the other player

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

        # Start a new thread for the connected player
        start_new_thread(threaded_client, (conn, currentPlayer))
        currentPlayer += 1  # Increase player count for each connection

    except (OSError, Exception) as e:
        if not running:
            break
        else:
            print(f"Error accepting connection: {e}")

print("Server stopped.")
