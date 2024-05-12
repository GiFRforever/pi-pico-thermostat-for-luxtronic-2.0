from luxtronik import Luxtronik
from luxtronik.datatypes import Celsius
import json


class HeatPump:
    def __init__(self):
        try:  # load config
            with open("config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.json not found")

        try:
            self.ip: str = config["heatpump_ip"]
            self.port: int = int(config["heatpump_port"])
        except KeyError:
            raise KeyError("config.json is not valid. Check README.md for more info")
        print("HP IP:", self.ip, "PORT:", self.port)
        try:
            self.l = Luxtronik(self.ip, self.port)
        except Exception:
            raise Exception("Could not connect to heat pump")
        # self.l.read()

    def change_heating_temp_by(self, temp: float) -> None:
        # self.l.read()

        current: Celsius = self.l.parameters.get("ID_Einst_WK_akt")  # type: ignore Celsius type garanteed

        new: float = float(str(current)) + temp
        if new > 5:  # artificial restrictions
            new = 5
        elif new < -5:
            new = -5
        print("New heating temp:", new)
        self.l.parameters.set("ID_Einst_WK_akt", new)

        self.l.write()
