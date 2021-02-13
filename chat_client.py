from client import TCPClient, ON_MESSAGE, ON_CONNECTED
import sys

if not (len(sys.argv) == 3 and sys.argv[2].isdigit()):
    sys.exit(0)

client = TCPClient(ip=sys.argv[1], port=int(sys.argv[2]))


@client.on(ON_CONNECTED)
def on_connected(*args, **kwargs):
    print(f"Connected to {args}")


@client.on(ON_MESSAGE)
def on_new_message(*args, **kwargs):
    print(f"You have new message: {args}")


def main():
    print("Starting client...")
    client.start()
    while True:
        client.send(input(">>>"))


if __name__ == "__main__":
    main()
