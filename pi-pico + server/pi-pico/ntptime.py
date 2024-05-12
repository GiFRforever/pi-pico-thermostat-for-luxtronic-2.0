import utime
import machine

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "pool.ntp.org"
# The NTP socket timeout can be configured at runtime by doing: ntptime.timeout = 2
timeout = 2


def time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(timeout)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]

    EPOCH_YEAR = utime.gmtime(0)[0]
    if EPOCH_YEAR == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

    return val - NTP_DELTA


def settime(rtc, timezone_offset=0, daylight_saving_time=False):
    t = time()

    # Adjust time based on timezone offset
    offset = timezone_offset * 3600

    # Check if daylight saving time is in effect and adjust time accordingly
    if daylight_saving_time:
        dst_start = utime.mktime(
            (
                utime.localtime(t)[0],
                3,
                (31 - (5 * utime.localtime(t)[0] // 4 + 4) % 7),
                1,
                0,
                0,
                0,
                0,
                0,
            )
        )
        dst_end = utime.mktime(
            (
                utime.localtime(t)[0],
                10,
                (31 - (5 * utime.localtime(t)[0] // 4 + 1) % 7),
                1,
                0,
                0,
                0,
                0,
                0,
            )
        )

        if t >= dst_start and t < dst_end:
            offset += 3600  # Add 1 hour for

    tm = utime.localtime(t + offset)
    rtc.datetime((tm[0], tm[1], tm[2], (tm[6] + 1) % 7, tm[3], tm[4], tm[5], 0))
    #     print((tm[0], tm[1], tm[2], (tm[6] + 1)%7, tm[3], tm[4], tm[5], 0))

    return offset


# Example usage: settime(timezone_offset=5, daylight_saving_time=True)


__version__ = "0.1.0"
