import math


class MeasurementSystem:
    PX_PER_CM = 96 / 2.54   # 37.795 px/cm at 96 dpi
    PX_PER_MM = 96 / 25.4   # 3.7795 px/mm
    UNITS = ["cm", "mm", "px"]

    def __init__(self, unit="cm"):
        self._unit = unit

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        if value in self.UNITS:
            self._unit = value

    def px_to_unit(self, px):
        if self._unit == "cm":
            return px / self.PX_PER_CM
        if self._unit == "mm":
            return px / self.PX_PER_MM
        return float(px)

    def unit_to_px(self, value):
        if self._unit == "cm":
            return value * self.PX_PER_CM
        if self._unit == "mm":
            return value * self.PX_PER_MM
        return float(value)

    def format(self, px):
        value = self.px_to_unit(px)
        if self._unit == "px":
            return f"{int(round(value))} px"
        return f"{value:.1f} {self._unit}"

    def format_coord(self, x_px, y_px):
        return f"X: {self.format(x_px)}   Y: {self.format(y_px)}"

    def nice_step(self, visible_px_range, max_ticks=8):
        """Returns (step_px, label_decimals) for ruler tick marks."""
        if visible_px_range <= 0:
            return self.unit_to_px(1), 0

        range_units = self.px_to_unit(visible_px_range)
        raw = range_units / max_ticks
        if raw <= 0:
            return self.unit_to_px(1), 0

        mag = 10 ** math.floor(math.log10(max(raw, 1e-9)))
        norm = raw / mag if mag > 0 else raw

        if norm < 1.5:
            step_units = 1 * mag
        elif norm < 3.5:
            step_units = 2 * mag
        elif norm < 7.5:
            step_units = 5 * mag
        else:
            step_units = 10 * mag

        if step_units >= 1:
            decimals = 0
        elif step_units >= 0.1:
            decimals = 1
        else:
            decimals = 2

        return self.unit_to_px(step_units), decimals
