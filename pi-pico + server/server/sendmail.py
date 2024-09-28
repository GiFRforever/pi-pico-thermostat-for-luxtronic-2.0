import smtplib
import ssl
import excelmaker
import os
import json
import picturemaker

from hpcontrol import HeatPump
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMail:
    def __init__(self) -> None:
        try:  # load config
            with open("config.json", "r") as f:
                config: dict[str, str] = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.json not found")

        try:
            self.password: str = config["password"]
            self.sender_email: str = config["sender_email"]
            self.receiver_email: str = config["receiver_email"]
            self.smtp_server: str = config["smtp_server"]
            self.port: int = int(config["smtp_port"])
            self.min_temp: float = float(config["min_temp"])
            self.max_temp: float = float(config["max_temp"])

        except KeyError:
            raise KeyError("config.json is not valid. Check README.md for more info")

        try:
            self.hp = HeatPump()
        except Exception:
            print("HeatPump not available")
            self.hp_status = False
        else:
            self.hp_status = True

    def send_mail(
        self,
        file: str,
        control: bool = False,
        lower_bound_in: float | None = None,
        upper_bound_in: float | None = None,
    ) -> bool:
        if lower_bound_in is None:
            lower_bound: float = self.min_temp
        else:
            lower_bound = lower_bound_in
        if upper_bound_in is None:
            upper_bound: float = self.max_temp
        else:
            upper_bound = upper_bound_in
        control_pass: bool = control

        if file.endswith((".csv", ".xlsx")):
            return True
        picturemaker.make_picture((picturePath := file))
        maxTemp, maxTempCas, minTemp, minTempCas, avg = excelmaker.make_excel(
            file
        )  # make excel file from csv

        with open(file, "r") as f:
            data_points: int = len(f.readlines()) - 2

        if data_points < 230:
            control = False

        # file += ".xlsx"  # add extension
        filename: str = file.split("/")[-1]  # exract filename from path

        self.subject: str = f"""Teploty z {". ".join(filename.split("-")[::-1])}"""
        self.body: str = f"""Průměrná teplota byla {avg} °C
            Nejvyšší teplota {maxTemp} °C v {maxTempCas}
            Nejnižší teplota {minTemp} °C v {minTempCas}
            Ovládání {"zapnuto" if control_pass else "vypnuto"}
            {"Čerpadlo není dostupné" if not self.hp_status else ""}
            Data jsou v příloze"""

        file += ".xlsx"  # add extension
        filename: str = file.split("/")[-1]  # exract filename from path

        # Create a multipart self.message and set headers
        self.message: MIMEMultipart = MIMEMultipart()
        self.message["From"] = self.sender_email
        self.message["To"] = self.receiver_email
        self.message["Subject"] = self.subject
        self.message["Bcc"] = self.receiver_email  # Recommended for mass emails

        # Add body to email
        self.message.attach(MIMEText(self.body, "plain"))

        # Open csv file in binary mode
        with open(file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part: MIMEBase = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        with open(picturePath + ".png", "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part2: MIMEBase = MIMEBase("application", "octet-stream")
            part2.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        encoders.encode_base64(part2)

        # Add header as key/value pair to attachment part
        part.add_header("Content-Disposition", "attachment", filename=f"{filename}")
        part2.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"""{picturePath.split("/")[-1]}.png""",
        )
        # Add attachment to self.message and convert self.message to string
        self.message.attach(part)
        self.message.attach(part2)
        text: str = self.message.as_string()

        # Log in to server using secure context and send email
        context: ssl.SSLContext = ssl.create_default_context()

        try:
            if self.port == 587:  # starttls
                with smtplib.SMTP(self.smtp_server, self.port, timeout=5) as server:
                    server.starttls(context=context)
                    server.login(self.sender_email, self.password)
                    server.sendmail(self.sender_email, self.receiver_email, text)
                    os.replace(file, f"LOGGED/{filename}")
                    os.remove(picturePath + ".png")
                    return True
            elif self.port == 465:  # ssl
                with smtplib.SMTP_SSL(
                    self.smtp_server, self.port, context=context
                ) as server:
                    server.login(self.sender_email, self.password)
                    server.sendmail(self.sender_email, self.receiver_email, text)
                    os.replace(file, f"LOGGED/{filename}")
                    os.remove(picturePath + ".png")
                    return True
            else:
                raise ValueError("Port must be 587 or 465")
        except smtplib.SMTPException:
            return False
        finally:
            if control and self.hp_status:
                if avg <= lower_bound:
                    # increase temperature
                    self.hp.change_heating_temp_by(0.5)
                elif avg >= upper_bound:
                    # decrease temperature
                    self.hp.change_heating_temp_by(-0.5)


if __name__ == "__main__":
    try:
        for file in os.listdir("WIP"):
            try:
                if not file.endswith(".xlsx") and not file.endswith(".png"):
                    if SendMail().send_mail(f"WIP/{file}"):
                        print(f"Email sent for {file}")
                    else:
                        print(f"Failed to send email for {file}")
                else:
                    print(f"Email not sent for {file}")
            except Exception:
                print(f"Email failed to sent for {file}")
    except FileNotFoundError:
        print("WIP folder not found")
