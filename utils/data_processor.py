import pandas as pd
import sqlite3
import sys
import asyncio
from datetime import timedelta

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
        output["epoch_arrival_time"] = float(output["epoch_arrival_time"])
        if len(output.keys()) != len(COLS):
            return {}
    return output

def calculate_bandwidth(df, interval=5):
    start_time = df["epoch_arrival_time"].iloc[0]
    end_time = df["epoch_arrival_time"].iloc[-1]
    max_time = end_time - start_time
    if max_time < timedelta(seconds=interval):
        return 0
    else:
        frames_of_interest = df.loc[end_time - df.loc[:, "epoch_arrival_time"] < timedelta(seconds=interval), ["epoch_arrival_time", "frame_length"]]
        total_bytes = frames_of_interest.loc[:, "frame_length"].sum()
        time_interval = frames_of_interest["epoch_arrival_time"].iloc[-1] - frames_of_interest["epoch_arrival_time"].iloc[0]
        bandwidth = total_bytes / time_interval.total_seconds()
        return bandwidth


async def main():
    while True:
        frame = await create_frame()
        processed_dict = process_frame(frame)
        print(processed_dict)

if __name__ == "__main__":
    asyncio.run(main())
