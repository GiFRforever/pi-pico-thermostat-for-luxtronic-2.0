import umail
import json
import os
from hpcontrol import HeatPump
from graphmaker import makegraph


class SendMail:
    def __init__(self) -> None:
        try:  # load config
            with open("config.json", "r") as f:
                config = json.load(f)
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
            self.place: str = config["place"]
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
        lower_bound: float = None,
        upper_bound: float = None,
    ) -> bool:
        if lower_bound is None:
            lower_bound = self.min_temp
        if upper_bound is None:
            upper_bound = self.max_temp

        if file.endswith(".csv"):
            return True
        filename: str = file.split("/")[-1]  # exract filename from path

        with open(file, "r") as f:
            f.readline()
            data = f.read().split("\n")

        control_pass: bool = control
        if len(data) < 270:  # lower bound to disable control with few datapoints
            control = False

        maxTemp: float = 0
        maxTempCas: str = ""
        minTemp: float = 100
        minTempCas: str = ""
        avg: float = 0

        maildata: str = ""

        for line in data:
            try:
                time, temp = line.split(";")
                temp = float(temp.replace(",", "."))

                if temp > maxTemp:
                    maxTemp = temp
                    maxTempCas = time

                if temp < minTemp:
                    minTemp = temp
                    minTempCas = time

                avg += temp

                maildata += f"{time}: {temp:.2f} °C\n"
            except:
                pass

        avg /= len(data) - 2

        self.subject: str = (
            f"""Teploty z {". ".join(filename.split("-")[::-1])}: {self.place}"""
        )
        self.body: str = (
            "Průměrná teplota byla "
            + str(round(avg, 2))
            + " °C\nNejvyšší teplota "
            + str(maxTemp)
            + " °C v "
            + str(maxTempCas)
            + "\nNejnižší teplota "
            + str(minTemp)
            + " °C v "
            + str(minTempCas)
            + "\nOvládání "
        )

        if control_pass:
            self.body += "zapnuto"
        else:
            self.body += "vypnuto"

        if not self.hp_status:
            self.body += "\nČerpadlo nedostupné"

        self.body += "\n\nData:\n\n"
        self.body += makegraph(path=file, col=28, data=data)

        try:
            # Send email once after MCU boots up
            self.smtp = umail.SMTP(self.smtp_server, self.port, ssl=(self.port == 465))
            self.smtp.login(self.sender_email, self.password)
            self.smtp.to(self.receiver_email)
            self.smtp.write("From:" + self.place + "<" + self.sender_email + ">\n")
            self.smtp.write("Subject:" + self.subject + "\n\n")
            self.smtp.write(self.body)
            #             self.smtp.write(maildata)
            self.smtp.send()
            self.smtp.quit()
            return True
        except:
            return False
        finally:
            if self.hp_status and control:
                if avg <= lower_bound:
                    # increase temperature
                    self.hp.change_heating_temp_by(0.5)
                elif avg >= upper_bound:
                    # decrease temperature
                    self.hp.change_heating_temp_by(-0.5)


if __name__ == "__main__":
    try:
        for file in os.listdir("WIP"):
            if not file.endswith(".xlsx"):
                if SendMail().send_mail(f"WIP/{file}"):
                    print(f"Email sent for {file}")
    except FileNotFoundError:
        print("WIP folder not found")
