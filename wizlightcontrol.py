import asyncio
import time
from pywizlight import wizlight, PilotBuilder

ip = "192.168.8.115"

async def Lumos():
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(colortemp = 6500))
    await light.turn_on(PilotBuilder(brightness = 255))


async def Nox():
    light = wizlight(ip)
    await light.turn_off()
    

async def Incendio():
    light = wizlight(ip)
    await light.turn_on(PilotBuilder(scene = 29))#candlelight = 29
