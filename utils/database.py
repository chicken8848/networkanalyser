import sqlite3
import asyncio
from data_processor import *

async def main():
    try:
        con = sqlite3.connect("../data/database.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE NetworkTraffic(frame_length, source_address, destination_address, protocols, epoch_arrival_time)")
        cur.close()
        con.close()
    except Exception as e:
        print(e)
    while True:
        try:
            frame = await create_frame()
            processed_frame = process_frame(frame)
            if (processed_frame):
                insert = [processed_frame[i] for i in COLS]
                insert_tuple = tuple(insert)
                con = sqlite3.connect("../data/database.db")
                cur = con.cursor()
                cur.execute(f"INSERT INTO NetworkTraffic VALUES {insert_tuple}")
                con.commit()
                cur.close()
                con.close()
        except Exception as e:
            print(insert_tuple)
            print(e)

if __name__ == "__main__":
    asyncio.run(main())

