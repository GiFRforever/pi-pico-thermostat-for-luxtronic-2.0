class Base:
    """Base datatype, no conversions."""

    measurement_type = None

    def __init__(self, name, writeable=False):
        self.value = None
        self.name = name
        self.writeable = writeable

    def to_heatpump(self, value):
        """Convert a value into heatpump units."""
        return value

    def from_heatpump(self, value):
        """Convert a value from heatpump units."""
        return value

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class SelectionBase(Base):
    """Selection base datatype, converts from an to list of codes."""

    codes = {}

    @property
    def options(self):
        """Return List of all available options."""
        return [value for _, value in self.codes.items()]

    def from_heatpump(self, value):
        if value in self.codes:
            return self.codes.get(value)
        return None

    def to_heatpump(self, value):
        for index, code in self.codes.items():
            if code == value:
                return index
        return None


class Celsius(Base):  # 1
    """Celsius datatype, converts from and to Celsius."""

    measurement_type = "celsius"

    def from_heatpump(self, value):
        return value / 10

    def to_heatpump(self, value):
        return int(float(value) * 10)


class HeatingMode(SelectionBase):  # 1
    """HeatingMode datatype, converts from an to list of HeatingMode codes."""

    measurement_type = "selection"

    codes = {
        0: "Automatic",
        1: "Second heatsource",
        2: "Party",
        3: "Holidays",
        4: "Off",
    }


class HotWaterMode(SelectionBase):  # 1
    """HotWaterMode datatype, converts from an to list of HotWaterMode codes."""

    measurement_type = "selection"

    codes = {
        0: "Automatic",
        1: "Second heatsource",
        2: "Party",
        3: "Holidays",
        4: "Off",
    }


class Unknown(Base):  # 1
    """Unknown datatype, fallback for unknown data."""

    measurement_type = None
