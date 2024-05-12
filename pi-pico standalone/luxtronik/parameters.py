"""Parse luxtonik parameters."""

# import logging

from luxtronik.datatypes import (
    # Kelvin,
    Celsius,
    # CoolingMode,
    HeatingMode,
    HotWaterMode,
    # Hours,
    # MixedCircuitMode,
    # PoolMode,
    # SolarMode,
    Unknown,
    # VentilationMode,
)

# # LOGGER = logging.get# Logger("Luxtronik.Parameters")


class Parameters:
    """Class that holds all parameters."""

    parameters = {
        0: Unknown("ID_Transfert_LuxNet"),
        1: Celsius("ID_Einst_WK_akt", True),
        2: Celsius("ID_Einst_BWS_akt", True),
        3: HeatingMode("ID_Ba_Hz_akt", True),
        4: HotWaterMode("ID_Ba_Bw_akt", True),
    }

    def __init__(self, safe=True):
        """Initialize parameters class."""
        self.safe = safe
        self.queue = {}

    def parse(self, raw_data):
        """Parse raw parameter data."""
        for index, data in enumerate(raw_data):
            parameter = self.parameters.get(index, False)
            if parameter is not False:
                parameter.value = parameter.from_heatpump(data)
            else:
                ## LOGGER.warning("Parameter '%d' not in list of parameters", index)
                parameter = Unknown(f"Unknown_Parameter_{index}")
                parameter.value = parameter.from_heatpump(data)
                self.parameters[index] = parameter

    def _lookup(self, target, with_index=False):
        """Lookup parameter by either id or name."""
        if isinstance(target, int):
            if with_index:
                return target, self.parameters.get(target, None)
            return self.parameters.get(target, None)
        if isinstance(target, str):
            try:
                target = int(target)
                if with_index:
                    return target, self.parameters.get(target, None)
                return self.parameters.get(target, None)
            except ValueError:
                for index, parameter in self.parameters.items():
                    if parameter.name == target:
                        if with_index:
                            return index, parameter
                        return parameter
        # LOGGER.warning("Parameter '%s' not found", target)
        if with_index:
            return None, None
        return None

    def get(self, target):
        """Get parameter by id or name."""
        parameter = self._lookup(target)
        return parameter

    def set(self, target, value):
        """Set parameter to new value."""
        index, parameter = self._lookup(target, with_index=True)
        if index:
            if parameter.writeable or not self.safe:
                self.queue[index] = parameter.to_heatpump(value)
            else:
                # LOGGER.warning("Parameter '%s' not safe for writing!", parameter.name)
                pass
        else:
            # LOGGER.warning("Parameter '%s' not found", target)
            pass
