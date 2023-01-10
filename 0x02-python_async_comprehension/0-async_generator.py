#!/usr/bin/python3
""" Async generator of randoms """
import asyncio
import random

async def async_generator():
    for i in range(10):
        yield (random.random() * 10)
        await asyncio.sleep(1)
