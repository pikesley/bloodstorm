import asyncio
import gc
import secrets
from time import sleep

import machine
import network
import urequests

from st7789v2.screen import screen, size

intensity = 0.5

colours = {
    "high": (0, 255, 255),  # cyan,
    "in-range": (243, 150, 25),  # yellow
    "low": (255, 0, 255),  # magenta
}

symbols = {
    "Increasing fast": "a",
    "Increasing": "b",
    "Stable": "c",
    "Decreasing": "d",
    "Decreasing fast": "e",
}

limits = {"low": 3.9, "high": 10}
run_limit = 1000
colour = colours["in-range"]

for name, rgb in colours.items():
    colours[name] = [int(c * intensity) for c in rgb]


def connect():
    """Connect to wifi."""
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)  # noqa: FBT003
    wlan.connect(secrets.SSID, secrets.KEY)
    while not wlan.isconnected():
        print("Waiting for connection...")
        sleep(1)


def get_state(entity):
    """Get state."""
    url = f"{secrets.HA_HOST}/api/states/{entity}"
    response = urequests.get(
        url,
        headers={"Authorization": f"Bearer {secrets.BEARER_TOKEN}"},
        timeout=10,
    )
    try:
        return response.json()["state"]
    except KeyError as ke:
        raise ValueError from ke


def setup():
    """Initialise."""
    screen.clear()
    connect()


async def write_bg():
    """Write the blood-glucose score."""
    string_length = 0
    dots = "zxvx"
    global colour  # noqa: PLW0603

    while True:
        try:
            bg = get_state(secrets.SENSOR_ID)

            if float(bg) <= limits["low"]:
                colour = colours["low"]
            if float(bg) > limits["high"]:
                colour = colours["high"]

            bg = bg.replace(".", dots[0])
            dots = dots[1:] + dots[0]

        except (ValueError, OSError):
            bg = "...."

        if string_length != len(bg):
            screen.clear()
            string_length = len(bg)

        scale_factor = 8
        offset = 28
        if len(bg) > 3:  # noqa: PLR2004
            scale_factor = 6
            offset = 27

        screen.write_text(
            bg,
            x=offset,
            y=offset,
            colour=colour,
            scale_factor=scale_factor,
        )
        await asyncio.sleep_ms(100)
        gc.collect()


async def write_trend():
    """Write the trend."""
    while True:
        try:
            trend = get_state(secrets.TREND_ID)
        except (ValueError, OSError):
            trend = "Stable"

        screen.write_text(
            symbols[trend] * 4,
            x="centered",
            y=size["y"] - 40,
            colour=colour,
            scale_factor=3,
        )

        await asyncio.sleep_ms(100)
        gc.collect()


async def boot():
    """Restart."""
    count = 0
    while True:
        count += 1
        if count > run_limit:
            machine.reset()
        await asyncio.sleep_ms(100)


async def main():
    """Run."""
    tasks = [asyncio.create_task(write_bg()), asyncio.create_task(write_trend())]
    await asyncio.gather(*tasks)
