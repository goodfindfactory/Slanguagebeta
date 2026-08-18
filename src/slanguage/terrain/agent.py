
import math


class TerrainMapperAgent:
    def __init__(self, scale: float = 0.1):
        self.x = 0.0
        self.y = 0.0
        self.target_x = None
        self.target_y = None
        self.target_lat = None
        self.target_lon = None
        self.scale = scale

    def earth_to_grid(self, lat: float, lon: float) -> tuple[float, float]:
        return lon * self.scale, lat * self.scale

    def grid_to_earth(self, x: float, y: float) -> tuple[float, float]:
        return y / self.scale, x / self.scale

    def set_target(self, lat: float, lon: float) -> None:
        self.target_lat = lat
        self.target_lon = lon
        self.target_x, self.target_y = self.earth_to_grid(lat, lon)

    def clear_target(self) -> None:
        self.target_x = None
        self.target_y = None
        self.target_lat = None
        self.target_lon = None

    def step_toward_target(self) -> str:
        if self.target_x is None:
            return "NO_TARGET"

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.05:
            self.x = self.target_x
            self.y = self.target_y
            return "ARRIVED"

        step_size = min(0.3, dist)
        self.x += dx / dist * step_size
        self.y += dy / dist * step_size
        return "MOVING"

    def move_to_target(self, max_steps: int = 500) -> str:
        steps = 0
        while steps < max_steps:
            status = self.step_toward_target()
            if status in {"ARRIVED", "NO_TARGET"}:
                return status
            steps += 1
        return "MOVING"
