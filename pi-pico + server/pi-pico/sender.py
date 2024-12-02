import socket
import json

try:  # load config
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("config.json not found")

try:
    server_ip: str = config["server_ip"]
    server_port: int = int(config["server_port"])
    place: str = config["place"]
except KeyError:
    raise KeyError("config.json is not valid. Check README.md for more info")


# Set up the socket
# server_ip = "0.0.0.0"  # Replace with the IP address of server
# server_port = 3621  # Choose a port number. If changed here, change in pi-pico + server/server/receiver.py as well


def send(file: str, hpcontrol: bool = False):
    global server_ip
    global server_port
    global place
    # Your list
    with open(file, "r") as f:
        # Convert the list to bytes using pickle
        zasilka = (
            f"{file.split('/')[-1]}.{place}{'.HP' if hpcontrol else ''}\n{f.read()}"
        )

    try:
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            s.connect((server_ip, server_port))

            # Send the data
            s.sendall(bytes(zasilka, "utf-8"))

            # Close the socket
            s.close()

            return True

        except Exception as e:
            print(e)
            # Close the socket
            s.close()  # type: ignore
    except:
        pass
    return False


if __name__ == "__main__":
    import os

    for file in os.listdir("WIP"):
        print(f"Sending {file}")
        try:
            if send("WIP/" + file):
                print("Success")
            else:
                print("Failed")
        except FileNotFoundError:
            print("Failed")
