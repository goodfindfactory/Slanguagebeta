
import random


def _noise(lat: float, lon: float) -> float:
    seed = int(lat * 10000 + lon * 10000)
    return random.Random(seed).random()


def water_at(lat: float, lon: float) -> str | None:
    temp = abs(lat) / 90.0
    humidity = (abs(lon) % 60) / 60.0
    noise = _noise(lat, lon)

    if humidity > 0.85 or noise > 0.95:
        return "~"
    if humidity > 0.65 or noise > 0.80:
        return "w"
    if humidity > 0.55 and temp < 0.4:
        return '"'
    return None


def biome_at(lat: float, lon: float) -> str:
    water_tile = water_at(lat, lon)
    if water_tile:
        return water_tile

    temp = abs(lat) / 90.0
    humidity = (abs(lon) % 60) / 60.0
    noise = _noise(lat, lon)

    if temp < 0.15 and humidity > 0.5:
        return "%"
    if temp < 0.25 and humidity > 0.3:
        return "#"
    if temp < 0.25:
        return ","
    if temp < 0.45 and humidity < 0.3:
        return "."
    if temp > 0.75:
        return "*"
    if noise > 0.85:
        return "^"
    return "~"
