#!/bin/python3

import co2meter as co2
import hid
import time
from datetime import datetime

def run():
    try:
        mon = co2.CO2monitor()
    except Exception as e:
        print(e)
        print("Could not reach co2meter via usb. Aborting")
        
        devices = hid.enumerate()
        print(f"Found {len(devices)} HID devices:")
        for i, device in enumerate(devices):
            print(f"  Device {i}: {device}")
        return

    print(mon.info)

    while True:
        data = mon.read_data()
        print(data, flush=True)
        time.sleep(10)

run()
print()
