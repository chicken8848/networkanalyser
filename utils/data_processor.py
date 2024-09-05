import pandas as pd
import sqlite3
import sys
import asyncio

VAL_FIELD = {"Frame Length": "frame_length", "Source Address": "source_address", "Destination Address": "destination_address", "[Protocols in frame": "protocols", "Epoch Arrival Time": "epoch_arrival_time", "Sender IP address": "source_address", "Target IP address": "destination_address"}

COLS = ["frame_length", "source_address", "destination_address", "protocols", "epoch_arrival_time"]
async def create_frame():
    output = []
    while True:
        for line in sys.stdin:
            if line == "\n":
                return "".join(output)
            else:
                output.append(line)

def process_frame(frame):
    output = {}
    lines = frame.split("\n")
    for line in lines:
        if (line[0:4] == "    "):
            field = line.strip().split(": ")
            if field[0] in VAL_FIELD.keys():
                output[VAL_FIELD[field[0]]] = field[1]
    if (output):
        output["protocols"] = output["protocols"][:-1]
        output["frame_length"] = int(output["frame_length"].split(" ")[0])
        if len(output.keys()) != len(COLS):
            return {}
    return output


async def main():
    while True:
        frame = await create_frame()
        processed_dict = process_frame(frame)
        print(processed_dict)

if __name__ == "__main__":
    asyncio.run(main())
