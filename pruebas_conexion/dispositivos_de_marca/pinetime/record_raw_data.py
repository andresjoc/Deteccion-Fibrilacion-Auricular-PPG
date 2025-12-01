import time
import asyncio
import struct
import numpy as np
from bleak import BleakClient
import json

# -----------------------------------------------
# BLE CONFIG
# -----------------------------------------------
address = "c4:ce:dc:06:4d:89"
MODEL_NBR_UUID = "2A39"

metadata = {
    "infinitime_version": 1.14,
    "led_current_mA": 12,
    "delay_ms": 50,
    "description": "raw ppg capture (no filtering)"
}

# -----------------------------------------------
# LOG FILES
# -----------------------------------------------
timestamp = str(int(time.time()))
csv_file = open(f"{timestamp}_ppg_10hz.csv", "w")

csv_file.write("timestamp,ppg_value\n")
csv_file.flush()

with open(f"{timestamp}_metadata.json", "w") as metadata_file:
    metadata_file.write(json.dumps(metadata, indent=4))

# -----------------------------------------------
# DATA MERGING (NO DUPLICATES)
# -----------------------------------------------
def most_overlap_index(arr1, arr2):
    ind = None
    overlapped_size = 20
    for i in range(1, int(len(arr1) / 2)):
        diff_arr = arr1[i:] - arr2[:-i]
        zeros_count = len(diff_arr) - np.count_nonzero(diff_arr)
        if overlapped_size < zeros_count:
            ind = i
            overlapped_size = zeros_count
    return ind, overlapped_size


def diff_subset_range(arr1, arr2):
    diff_arr = (arr1 - arr2)[:-4]
    non_zero_indeces = np.nonzero(diff_arr)[0]
    return (min(non_zero_indeces), max(non_zero_indeces))


def add_new_data(aggregated_data, arr1, arr2):
    ind, zeros = most_overlap_index(arr1, arr2)

    if ind:
        bad_ending_count = -(64 - ind - zeros)
        aggregator_striped = aggregated_data[:bad_ending_count] if bad_ending_count < 0 else aggregated_data
        new_values = arr2[-ind:]
        result = np.append(aggregator_striped, new_values)
    else:
        inds = diff_subset_range(arr1, arr2)
        new_values = arr2[inds[0]:inds[1]+1]
        result = np.append(aggregated_data, new_values)

    return result, new_values


# -----------------------------------------------
# BLE DATA GENERATOR
# -----------------------------------------------
async def main(address):
    async with BleakClient(address) as client:
        while True:
            raw_data = await client.read_gatt_char(MODEL_NBR_UUID)
            int_array = np.array(list(struct.unpack('<64H', raw_data)))
            yield int_array
            await asyncio.sleep(1)


# -----------------------------------------------
# SAVE ONLY NEW SAMPLES
# -----------------------------------------------
def save_ppg(new_values):
    now = time.time()
    for v in new_values:
        csv_file.write(f"{now},{v}\n")
    csv_file.flush()


# -----------------------------------------------
# PROCESS LOOP
# -----------------------------------------------
async def process(data_generator):
    last_data = await anext(data_generator)
    aggregated = last_data

    async for data in data_generator:
        arr1 = last_data
        arr2 = data
        last_data = arr2

        aggregated, new_values = add_new_data(aggregated, arr1, arr2)
        save_ppg(new_values)


# -----------------------------------------------
# RUN EVERYTHING 
# -----------------------------------------------
async def runner():
    gen = main(address)
    await process(gen)

if __name__ == "__main__":
    try:
        asyncio.run(runner())
    finally:
        csv_file.close()
