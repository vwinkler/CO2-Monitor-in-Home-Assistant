#!/bin/python3

import co2meter as co2
import time
from datetime import datetime

def run():
    try:
        mon = co2.CO2monitor()
    except Exception as e:
        print(e)
        print("Could not reach co2meter via usb. Aborting")
        return

    print(mon.info)

    while True:
        data = mon.read_data()
        print(data)
        time.sleep(10)

run()
print()
