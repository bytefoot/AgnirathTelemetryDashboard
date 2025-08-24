import serial
import json
import os
import csv
import numpy as np


# SERIAL_PORT = "/dev/ttyUSB1"
SERIAL_PORT = "/dev/tty.usbserial-0001"
BAUD_RATE = 115200
TIMEOUT = 1
HEADER = b'\xDE\xAD\xBE\xEF'  ## same HEADER as sender ##

logpath = "/Users/kevinkinsey/Developer/Agnirath/d2/log"


def generate_crc(byte_stream: bytes, poly=0x1021, init_val=0x0000):
    """Generate CRC-16-CCITT (XModem) [2 bytes] for the byte_stream"""
    crc = init_val
    for byte in byte_stream:
        crc ^= byte << 8
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF  # Keep it 16-bit
    return crc.to_bytes(2, byteorder='little')


def flush_serial(ser):
    while ser.in_waiting > 0:
        ser.read(ser.in_waiting)


prev = None

def read_packet(ser: serial.Serial):
    global prev
    head_bytes = ser.read(len(HEADER))
    if head_bytes != HEADER:
        # print("header mismatch, dropping packet")
        flush_serial(ser)
        return None

    length_bytes = ser.read(2)
    if len(length_bytes) < 2:
        return None  # timeout or incomplete

    length = int.from_bytes(length_bytes, 'little')

    crc_bytes = ser.read(2)
    if len(crc_bytes) < 2:
        return None

    type_byte = ser.read(1)
    if len(type_byte) < 1:
        return None

    data_bytes = ser.read(length)
    if len(data_bytes) < length:
        return None

    calc_crc = generate_crc(type_byte + data_bytes)
    if calc_crc != crc_bytes:
        print("CRC check failed, dropping packet")
        if prev:
            print(*prev)
        print(type_byte.decode(), data_bytes.hex(), len(data_bytes))
        flush_serial(ser)
        return None

    prev = (type_byte.decode(), data_bytes.hex(), len(data_bytes))

    return {
        "type": type_byte.decode(),
        "data": data_bytes
    }


def unpack_flags(flag_bytes: bytes, total_bits: int, flags_list: list[str]) -> dict:
    bits = []
    for byte in flag_bytes:
        for bit_pos in range(8):
            bits.append(bool(byte & (1 << bit_pos)))
    bits = bits[:total_bits]  # truncate to exact flag count

    flag_values = {}
    for i, flag_key in enumerate(flags_list):
        # print(bits, len(bits), i, flag_key)
        flag_values[flag_key] = bits[i]
    return flag_values


def reverse_bytestream(data_bytes: bytes, output_order: list[str], fields: dict, flags: list[str], type_map: dict):
    data_buf = {}
    idx = 0

    for key in output_order:
        type_str = fields[key]["type"]

        if key == "Flags":
            total_bits = int(type_str.split("-")[1])
            num_bytes = (total_bits + 7) // 8
            flag_bytes = data_bytes[idx:idx+num_bytes]
            idx += num_bytes

            flag_values = unpack_flags(flag_bytes, total_bits, flags)
            data_buf.update(flag_values)

        else:
            dtype = type_map[type_str]
            size = dtype(0).nbytes  # numpy dtype size in bytes

            val_bytes = data_bytes[idx:idx+size]
            idx += size

            # Convert bytes back to numpy value
            value = np.frombuffer(val_bytes, dtype=dtype)[0]
            data_buf[key] = value.item() * fields[key].get("multiplier", 1)

    return data_buf


# def log_data(data_buf, filename="output_data1.jsonl"):
#     # Convert numpy scalars to Python native types ####################### temp fix #####TODO: fix this
#     clean_data = {k: (v.item() if hasattr(v, 'item') else v) for k, v in data_buf.items()}
#     with open(filename, "a") as f:
#         json_line = json.dumps(clean_data)
#         f.write(json_line + "\n")

def log_data(data_buf, type):
    # Convert numpy scalars to Python native types
    clean_data = {k: (v.item() if hasattr(v, 'item') else v) for k, v in data_buf.items()}
    filename=f"{logpath}/output_data_{type}.csv"
    
    # Check if file exists and has content
    file_exists = os.path.isfile(filename)
    file_empty = not file_exists or os.path.getsize(filename) == 0
    
    # Get existing headers or use current keys
    if file_exists and not file_empty:
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Read existing header
    else:
        headers = list(clean_data.keys())  # Use current keys as header
    
    # Prepare row data matching header order
    row_data = [clean_data.get(header, '') for header in headers]
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        # Write header only for new/empty files
        if file_empty:
            writer.writerow(headers)
        writer.writerow(row_data)

def main(queue, loop):
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)

    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, 'packet_structure.json')

    with open(json_path, 'r') as f:
        structure = json.load(f)

    flags = structure["Flags"]
    fields = structure["Fields"]
    type_map = {
        "float16": np.float16,
        "float32": np.float32,
        "int16": np.int16,
        "int32": np.int32,
        "bool": bool
    }

    sym = ('*', '#')
    i = 0

    while True:
        packet = read_packet(ser)
        if packet is None:
            continue
        print(f"[{sym[i]}] Received packet type: {packet['type']} data length: {len(packet['data'])}")
        i = (i + 1) % 2

        data_buf = None
        
        if packet['type'] == 'A':
            data_buf = reverse_bytestream(
                packet['data'], structure['Output_Order_A'],
                fields, flags, type_map
            )

            net_solar_power = 0
            for l in ('A', 'B', 'C', 'D'):
                data_buf[f'Power_{l}'] = data_buf[f'Output_Voltage_{l}'] * data_buf[f'Output_Current_{l}']
                net_solar_power += data_buf[f'Power_{l}']
            data_buf[f'Solar_Power'] = net_solar_power

            data_buf['Bus_Power'] = data_buf['Bus_Voltage'] * data_buf['Bus_Current']
            print(data_buf["Throttle_Perc"])

        elif packet['type'] == 'B':
            data_buf = reverse_bytestream(
                packet['data'], structure['Output_Order_B'],
                fields, flags, type_map
            )

        else:
            print(f"Type is {packet['type']}, doesn't match any known type")
            continue

        loop.call_soon_threadsafe(queue.put_nowait, (packet['type'], data_buf))

        log_data(data_buf, packet['type'])


if __name__ == "__main__":
    main()
