"""luxtonik heatpump interface."""

# -*- coding: utf-8 -*-

# import logging
import socket
import struct

# from luxtronik.calculations import Calculations
from luxtronik.parameters import Parameters

# from luxtronik.visibilities import Visibilities

# LOGGER = logging.getLogger("Luxtronik")


class Luxtronik:
    """main luxtronik class."""

    def __init__(self, host, port, safe=True):
        self._host = host
        self._port = port
        self._socket = None
        # self.calculations = Calculations()
        self.parameters = Parameters(safe=safe)
        # self.visibilities = Visibilities()
        self.read()

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))
        print("Connected to Luxtronik heatpump", self._host, ":", self._port)

    def _disconnect(self):
        self._socket.close()
        print("Disconnected from Luxtronik heatpump", self._host, ":", self._port)

    def read(self):
        """Read data from heatpump."""
        self._connect()
        self._read_parameters()
        # self._read_calculations()
        # self._read_visibilities()
        self._disconnect()

    def write(self):
        """Write patameter to heatpump."""
        self._connect()
        for index, value in self.parameters.queue.items():
            if not isinstance(index, int) or not isinstance(value, int):
                print("Parameter id '%s' or value '%s' invalid!", index, value)
                continue
            print("Parameter '%d' set to '%s'", index, value)
            data = struct.pack(">iii", 3002, index, value)
            # LOGGER.debug("Data %s", data)
            self._socket.sendall(data)
            cmd = struct.unpack(">i", self._socket.recv(4))[0]
            # LOGGER.debug("Command %s", cmd)
            val = struct.unpack(">i", self._socket.recv(4))[0]
            # LOGGER.debug("Value %s", val)
        self._disconnect()
        # flush queue after writing all values
        self.parameters.queue = {}

    def _read_parameters(self):
        data = []
        self._socket.sendall(struct.pack(">ii", 3003, 0))
        cmd = struct.unpack(">i", self._socket.recv(4))[0]
        print("Command", cmd)
        length = struct.unpack(">i", self._socket.recv(4))[0]
        length = 5
        print("Length", length)
        for _ in range(0, length):
            try:
                data.append(struct.unpack(">i", self._socket.recv(4))[0])
            except struct.error as e:
                # not logging this as error as it would be logged on every read cycle
                # print(e)
                pass
        print("Read", length, "parameters")
        self.parameters.parse(data)
