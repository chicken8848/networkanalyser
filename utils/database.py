import sqlite3
import asyncio
from data_processor import *

async def main():
    con = sqlite3.connect("../data/database.db")
    try:
        cur = con.cursor()
        cur.execute("CREATE TABLE NetworkTraffic(frame_length, source_address, destination_address, protocols, epoch_arrival_time)")
        cur.close()
    except Exception as e:
        print(e)
    try:
        while True:
            frame = await create_frame()
            processed_frame = process_frame(frame)
            print(processed_frame)
            if (processed_frame):
                insert = [processed_frame[i] for i in COLS]
                insert_tuple = tuple(insert)
                print(insert_tuple)
                cur = con.cursor()
                cur.execute(f"INSERT INTO NetworkTraffic VALUES {insert_tuple}")
                con.commit()
                cur.close()
            else:
                print("frame dropped")
    except Exception as e:
        con.close()
        print(e)
        print("shutting down")

if __name__ == "__main__":
    asyncio.run(main())

