from sendmail import SendMail


def send(file: str, hpcontrol: bool = False):
    return SendMail().send_mail(file, control=hpcontrol)


if __name__ == "__main__":
    import os

    for file in os.listdir("WIP"):
        print(f"Sending {file}")
        try:
            if send("WIP/" + file):
                print("Success")
            else:
                print("Failed")
        except FileNotFoundError as e:
            print("Failed")
