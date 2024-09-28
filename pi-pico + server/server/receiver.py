import socket
import threading
import sendmail
import os
import time
from random import uniform


def handle_client(cwd, conn, addr) -> None:
    with conn:
        print(f"Connected by {addr}")

        # Receive the data
        data: list = []
        while True:
            packet = conn.recv(4096)
            if not packet:
                break
            data.append(packet)

        zasilka: bytes = b"".join(data)
        received_list: str = zasilka.decode("utf-8")

        info, rest = received_list.split("\n", 1)
        if info.endswith("HP"):
            name: str = info[:-3]
            hpcontrol = True
        else:
            name = info
            hpcontrol = False
        print(f"Received {name}")
        with open(f"{cwd}/WIP/{name}", "w") as f:
            f.write(rest)

    for _ in range(5):
        if sendmail.SendMail().send_mail(f"{cwd}/WIP/{name}", control=hpcontrol):
            print(f"{name}: good")
            os.rename(f"{cwd}/WIP/{name}", f"{cwd}/LOGGED/{name}.csv")
            break
        else:
            time.sleep(uniform(5, 15))

    else:
        print(f"{name}: bad")


# Set up the socket
host: str = ""  # Replace with the IP address of pi pico, leave empty for any
port = 3621  # Choose a port number. If changed here, change in pi-pico + server/pi-pico/sender.py as well
cwd: str = os.getcwd()
print(cwd)

if __name__ == "__main__":
    try:
        for file in os.listdir("WIP"):
            try:
                if not file.endswith(".xlsx") and not file.endswith(".png"):
                    if sendmail.SendMail().send_mail(f"{cwd}/WIP/{file}"):
                        print(f"Email sent for {file}")
                        os.rename(f"{cwd}/WIP/{file}", f"{cwd}/LOGGED/{file}.csv")
            except Exception:
                print(f"Email not sent for {file}")
    except FileNotFoundError:
        print("WIP folder not found")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print("Waiting for connections...")

        while True:
            conn, addr = s.accept()

            # Handle each connection in a separate thread
            threading.Thread(target=handle_client, args=(cwd, conn, addr)).start()
