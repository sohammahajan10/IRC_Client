import socket
import threading
import sys

SERVER = "irc.libera.chat"
PORT = 6667
NICK = "TestUser12345"

current_channel = "#libera"
connected = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))

print("Connected to server")

# Handshake
sock.sendall(f"NICK {NICK}\r\n".encode())
sock.sendall(f"USER {NICK} 0 * :{NICK}\r\n".encode())

# Join initial channel
sock.sendall(f"JOIN {current_channel}\r\n".encode())
print(f"Joined {current_channel}")


def listen_to_server():
    global connected
    while connected:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server")
                connected = False
                break

            message = data.decode(errors="ignore")
            print(message, end="")

            # PING → PONG
            if message.startswith("PING"):
                sock.sendall(message.replace("PING", "PONG", 1).encode())

        except:
            connected = False
            break


# Start server listener
threading.Thread(target=listen_to_server, daemon=True).start()

# User input loop
while connected:
    try:
        sys.stdout.write("> ")
        sys.stdout.flush()

        user_input = sys.stdin.readline().strip()
        if not user_input:
            continue

        if user_input.startswith("/join "):
            new_channel = user_input.split(" ", 1)[1]
            if not new_channel.startswith("#"):
                print("Channel must start with #")
                continue

            current_channel = new_channel
            sock.sendall(f"JOIN {current_channel}\r\n".encode())
            print(f"Joined {current_channel}")

        elif user_input == "/quit":
            sock.sendall(b"QUIT :Client exiting\r\n")
            print("Exiting...")
            connected = False
            break

        else:
            # Normal message
            sock.sendall(
                f"PRIVMSG {current_channel} :{user_input}\r\n".encode()
            )

    except:
        break

sock.close()
