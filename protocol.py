from enum import Enum
from time import sleep
from generate import play_message
import random

from record import listen_until_timeout


class Status(Enum):
    AwaitingContact = 0
    Contacted = 1
    FoundFriend = 2
    InContact = 3


baud_rate_test = "abcdefghijklmn"  # opqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class Unit:
    status = Status.AwaitingContact
    baud_rate = 2
    role = None

    def __init__(self):
        pass

    def play_message(self, message, baud_rate=None):
        print(f"Playing message: {message}")
        play_message(message, baud_rate or self.baud_rate)

    def await_contact(self):
        while True:
            duration = 2 + random.random() * 10
            print(f"Listening for contact for {duration:.2f} seconds ...")
            result = self.listen_until_timeout(duration)
            print(result)

            if len(result) > 0:
                if result[0] == "0":
                    print("Found a friend!")
                    self.status = Status.FoundFriend
                    return
                elif result[0] == "1":
                    print("Contacted!")
                    self.status = Status.Contacted
                    return

            print("No contact, trying to contact ...")
            self.play_message("0", 2)

    def contacted(self):
        print("Contacted!")

        for _ in range(3):
            self.play_message("2", 2)

        while True:
            self.play_message("2", 2)
            result = self.listen_until_timeout(3)
            if len(result) > 0 and result[0] == "3":
                print("Successfully contacted!")

                self.role = "slave"

                self.status = Status.InContact
                return

    def found_friend(self):
        print("Found friend!")

        for _ in range(2):
            self.play_message("1", 2)

        while True:
            self.play_message("1", 2)
            sleep(2)
            result = self.listen_until_timeout(6)

            if len(result) > 0 and result[0] == "2":
                print("Successfully contacted!")

                sleep(2)
                self.play_message("3", 2)
                self.role = "master"

                self.status = Status.InContact

                return

    def play_until_ack(self, message, timeout=3):
        while True:
            self.play_message(message)
            result = self.listen_until_timeout(timeout)

            print("Ack result", result)

            if len(result) > 0 and result == ":A":
                return

    def ack(self):
        self.play_message(":A")

    def master(self):
        sleep(2)
        baud_max = 8
        baud_min = 0.1
        baud_rate = 2

        while True:
            self.play_until_ack(":B", timeout=10)
            sleep(1)
            self.play_message(baud_rate_test, baud_rate)

            if self.listen_until_timeout(10) == "BRTOK":
                print("Baud rate test successful!")
                baud_min = baud_rate
                baud_rate = (baud_max + baud_min) // 2
            else:
                print("Baud rate test failed!")
                baud_max = baud_rate
                baud_rate = (baud_max + baud_min) // 2

            if baud_max - baud_min <= 1:
                break

        while True:
            print("We are rolling!", baud_max, baud_min)
            sleep(100)

    def slave(self):
        while True:
            command = self.listen_until_timeout(60)
            sleep(1)
            if command.startswith(":BAUD="):
                self.baud_rate = int(command[6:])
                self.ack()
            elif command == "?WHO":
                self.ack()
                self.play_message("I am a slave")
            elif command == ":B":
                self.ack()
                result = self.listen_until_timeout(100)
                print("Baud rate result", result)
                sleep(1)
                if result.strip() == baud_rate_test.strip():
                    self.play_message("BRTOK")
                else:
                    self.play_message("BRTFAIL")
            else:
                print("Unknown command", command)

    def in_contact(self):
        print("In contact!", self.role)

        if self.role == "master":
            self.master()
        elif self.role == "slave":
            self.slave()

    def listen_until_timeout(self, timeout: int):
        result = []

        for x in listen_until_timeout(timeout):
            print("REC:", x)
            result.append(x)

        return "".join(result)

    def run(self):
        while True:
            if self.status == Status.AwaitingContact:
                self.await_contact()
            elif self.status == Status.Contacted:
                self.contacted()
            elif self.status == Status.FoundFriend:
                self.found_friend()
            elif self.status == Status.InContact:
                self.in_contact()


def main():
    unit = Unit()
    try:
        unit.run()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
