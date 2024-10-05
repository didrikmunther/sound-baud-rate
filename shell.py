import sys
from generate import play_message
from record import listen_until_stop


def send(message: str):
    play_message(message)


def receive():
    for x in listen_until_stop():
        sys.stdout.write(x)
        sys.stdout.flush()

    sys.stdout.flush()


def main():
    while True:
        print("(s)end or (r)ecieve?")
        sys.stdout.flush()
        mode = input().lower()
        if mode == "s":
            print("Enter message:")
            sys.stdout.flush()
            message = input()
            print("Sending message...")
            sys.stdout.flush()
            send(message)
        elif mode == "r":
            print("Receiving message...")
            sys.stdout.flush()
            receive()
        else:
            print("Invalid mode, try again.")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
