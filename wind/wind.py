from pymodbus.client import ModbusSerialClient
import time

# Create RTU client
client = ModbusSerialClient(
    # method="rtu",
    port="/dev/tty.usbserial-BG0113FT",
    baudrate=4800,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

if client.connect():
    print("Connected to wind sensor on COM5")
    print("Reading continuously... (Press Ctrl+C to stop)")
    
    try:
        while True:
            # Read 2 registers: wind speed (0) and direction (1)
            result = client.read_holding_registers(address=0, count=2, unit=1)
            if not result.isError():
                wind_speed_raw = result.registers[0]
                wind_dir_raw = result.registers[1]

                wind_speed = wind_speed_raw / 100.0  # scaling per datasheet
                wind_direction = wind_dir_raw       # 0–360 degrees

                print(f"Wind speed: {wind_speed:.2f} m/s | Wind direction: {wind_direction}°")
                with open("log.log", 'a+') as file:
                    file.write(f"Wind speed: {wind_speed:.2f} m/s | Wind direction: {wind_direction}°")
            else:
                print("Modbus error:", result)
            
            time.sleep(1)  # Wait 1 second between readings
            
    except KeyboardInterrupt:
        print("\nStopping wind sensor readings...")
    finally:
        client.close()
        print("Connection closed")
else:
    print("Unable to connect to COM5")
