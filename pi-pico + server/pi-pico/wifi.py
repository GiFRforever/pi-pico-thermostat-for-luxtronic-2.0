import network
import utime


class WiFi:
    def __init__(self, *, ssid, password):
        # Your network credentials
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        if self.wlan.status() == 3:
            return

        # Connect to Wi-Fi
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)

        # Wait for connection to establish
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print("waiting for connection...", self.wlan.status())
            utime.sleep(5)

        # Manage connection errors
        if self.wlan.status() != 3:
            raise RuntimeError("Network Connection has failed")
        else:
            # pass
            print("Connected to", self.ssid)

    def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)


if __name__ == "__main__":
    wifi = WiFi(ssid="ssid", password="password")
    wifi.connect()
    print(wifi.wlan.status())
