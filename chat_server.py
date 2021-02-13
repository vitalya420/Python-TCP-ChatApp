from server import TCPServer, NEW_MESSAGE, NEW_CONNECTION
import sys

if not (len(sys.argv) == 3 and sys.argv[2].isdigit()):
    sys.exit(0)

server = TCPServer(ip=sys.argv[1], port=int(sys.argv[2]))


@server.on(NEW_CONNECTION)
def on_incoming_connection(*args, **kwargs):
    print(f"New connection established {args}")


@server.on(NEW_MESSAGE)
def on_new_message(addr, message, **kwargs):
    print(f"Message from addr {addr}: {message}")
    server.broadcast(message)


def main():
    print("Starting server...")
    server.start()
    print("Server started! Waiting for incoming connections!")


if __name__ == "__main__":
    main()
