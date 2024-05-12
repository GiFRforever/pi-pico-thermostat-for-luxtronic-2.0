import readtemp, ntptime, wifi, sender, time, os, json
import machine, utime  # type: ignore pi pico specific imports

led = machine.Pin("LED", machine.Pin.OUT)
t_off = 1
dst = True

led.value(1)
utime.sleep(0.1)
led.value(0)

HPCONTROLL = True

try:  # load config
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("config.json not found")

try:
    wifi_ssid: str = config["ssid"]
    wifi_passwd: str = config["wifipasswd"]
except KeyError:
    raise KeyError("config.json is not valid. Check README.md for more info")

try:
    wifi = wifi.WiFi(ssid=wifi_ssid, password=wifi_passwd)
    wifi.connect()
    rtc = machine.RTC()
    offset = ntptime.settime(rtc, timezone_offset=t_off, daylight_saving_time=dst)
except Exception as e:
    print(e)
    led.value(1)
    utime.sleep(1)
    led.value(0)
    machine.reset()


def actual_time(yesterday=False, sync=False):
    if not sync and not yesterday:
        r = rtc.datetime()
        return (r[0], r[1], r[2], r[4], r[5], r[6], r[3], None)

    global offset
    wifi.connect()
    for _ in range(3):
        try:
            return time.localtime(ntptime.time() + offset - (86400 if yesterday else 0))
        except:
            try:
                wifi.connect()
                offset = ntptime.settime(
                    rtc, timezone_offset=t_off, daylight_saving_time=dst
                )
            except:
                pass

    machine.reset()


utime.sleep(1)
for _ in range(rtc.datetime()[4]):
    led.value(1)
    utime.sleep(0.3)
    led.value(0)
    utime.sleep(0.3)

try:
    t_sensor = readtemp.MCP9808()
    t_sensor.read_temp()
except Exception as e:
    print(e)
    for _ in range(5):
        led.value(1)
        utime.sleep(0.2)
        led.value(0)
        utime.sleep(0.2)
    machine.reset()


def send_command() -> None:
    global today
    wifi.connect()
    yesterday = "-".join(
        [f"{x:0>2}" for x in actual_time(yesterday=True, sync=True)[0:3]]
    )
    today = "-".join([f"{x:0>2}" for x in actual_time()[0:3]])
    if (dir_wip := os.listdir("WIP")) != []:
        for file in dir_wip:
            if file != today:
                print("Sending", file)
                if sender.send(
                    f"WIP/{file}", (HPCONTROLL if file == yesterday else False)
                ):
                    os.rename(f"WIP/{file}", f"LOGGED/{file}.csv")
                    print("Send successful")
                else:
                    print("Encoutered problem")
    if today not in dir_wip:
        with open(f"WIP/{today}", "w") as f:
            f.write("Time;Temperature\n")
    if (d := len((l := os.listdir("LOGGED")))) > 30:  # remove files if over 30
        for i in range(d - 30):
            os.remove(f"LOGGED/{l[i]}")
    wifi.disconnect()


today = "-".join([f"{x:0>2}" for x in actual_time(sync=True)[0:3]])
send_command()  # send all old files from WIP folder and prepare today's file

utime.sleep(1)
led.value(1)
utime.sleep(0.1)
led.value(0)
utime.sleep(0.1)


def main_logger():
    global offset
    while True:
        teplota: float = t_sensor.read_temp()
        now = actual_time()
        temp = ":".join([f"{x:0>2}" for x in now[3:5]]) + ";" + str(round(teplota, 2))
        print(temp, end="\r")
        if now[3:5] == (0, 0):  # midnight
            wifi.connect()
            send_command()
            offset = ntptime.settime(timezone_offset=t_off, daylight_saving_time=dst)
        if now[4] % 5 == 0:  # every 5 minutes
            with open(f"WIP/{today}", "a") as f:
                f.write(f"{temp}\n")
        utime.sleep(61 - now[5])


if __name__ == "__main__":
    # main_logger()
    try:
        main_logger()
    except Exception as e:
        print(e)
        for _ in range(3):
            led.value(1)
            utime.sleep(0.3)
            led.value(0)
        for _ in range(3):
            led.value(1)
            utime.sleep(1)
            led.value(0)
        machine.reset()
