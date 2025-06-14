from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta, timezone
import uvicorn
from contextlib import asynccontextmanager
import threading
import traceback
from pprint import pprint 

from downlink import main as run_downlink

# Key Lists
PACKET_A_DIRECT_KEYS = ("SOC_Ah", "Pack_Voltage", "Pack_Current", "Bus_Voltage",
                        "Bus_Current", "Motor_Velocity", "PhaseC_Current",
                        "PhaseB_Current", "Speed",)
MPPT_NAMES = ('A', 'B', 'C', 'D')
MPPT_VALUE_KEYS = ("Input_Voltage", "Input_Current",
                        "Output_Voltage", "Output_Current")
MPPT_FLAG_NAMES = ('hw_overvolt', 'hw_overcurrent', 'under12v', None,
                     'low_array_power', 'battery_full', 'battery_low',
                     'mosfet_overheat', )
CONTACTOR_FLAG_NAMRS = (
    'contactor1_error', 'contactor2_error',
    'contactor1_output', 'contactor2_output',
    'contactor_supply',
    'contactor3_error', 'contactor3_output',
    None
)
BMS_FLAG_NAMES = (
    "cell_over_voltage", "cell_under_voltage", "cell_over_temp",
    "measurement_untrusted", "cmu_comm_timeout", "vehicle_comm_timeout",
    "bms_setup_mode", "cmu_can_status", "isolation_test_fail", "soc_invalid",
    "can_supply_low", "contactor_not_engaged", "extra_cell_detected",
)
MOTOR_LIMIT_NAMES = (
    'ipm_temp_limit', 'bus_voltage_lower_limit',
    'bus_voltage_upper_limit', 'bus_current_limit',
    'velocity_limit', 'motor_current_limit',
    'output_voltage_pwm_limit',
)
MOTOR_ERROR_NAMES = (
    'hardware_over_current','software_over_current', 'dc_bus_over_voltage', 
    'bad_motor_position', 'watchdog_reset', 'config_read_error',
    'rail_15v_uvlo', 'desaturation_fault', 'motor_over_speed', 
)
CABIN_FLAG_NAMES = (  ## TODO
    'Cabin_CO_Content', 'Cabin_CH4_Content',
    'Cabin_NH3_Content', 'Cabin_NO2_Content',
    'Cabin_O2_Content', 'Cabin_Temperature',
    'Cabin_Pressure', 'Cabin_CO2_Content',
)
PACKET_B_DIRECT_KEYS = ("Motor_Temp", "HeatSink_Temp", "DSP_Board_Temp",)


# Global state to store current data
current_data = {
    "metric": {
        'Pack_Voltage': 48.2,
        'SOC_Ah': 12000,
        'power_consumption': 1250.0,
        'solar_input': 450.0,
        'distance_travelled': 142.8,
        'Motor_Temp': 68.5,
        'Speed': 65.4,
        'predicted': 67.2,

        'Pack_Current': 46.26,
        'cmus': [{
            'temperature': 30.12,
            'cell_temperature': 30.12,
            'cell_voltages': [3.7 for _ in range(8)]
        } for _ in range(5)],
        'battery_ranges': {
            'min_temp': 0,
            'max_temp': 0,
            'min_volt': 0,
            'max_volt': 0,
        },
        'precharge_state': 0,
        'contactor_flags': {
            'contactor1_error': False,
            'contactor2_error': False,
            'contactor3_error': False,
            'contactor1_output': False,
            'contactor2_output': False,
            'contactor3_output': False,

            'contactor_supply': False,
        },
        'bmsFlags': {
            'cell_over_voltage': False,
            'cell_under_voltage': False,
            'cell_over_temp': False,
            'measurement_untrusted': False,
            'cmu_comm_timeout': False,
            'vehicle_comm_timeout': False,
            'bms_setup_mode': False,
            'cmu_can_status': False,
            'isolation_test_fail': False,
            'soc_invalid': False,
            'can_supply_low': False,
            'contactor_not_engaged': False,
            'extra_cell_detected': False,
        },


        'Motor_Velocity': 123,
        'Speed2': 75,
        'HeatSink_Temp': 31,
        'PhaseA_Current': 45.65,
        'PhaseB_Current': 45.6,
        'PhaseC_Current': 45.7,
        'Bus_Voltage': 50,
        'Bus_Current': 45,
        'Bus_Power': 50 * 45,
        'DSP_Board_Temp': 0,
        'MotorLimits': {
            'ipm_temp_limit': False,
            'bus_voltage_lower_limit': False,
            'bus_voltage_upper_limit': False,
            'bus_current_limit': False,
            'velocity_limit': False,
            'motor_current_limit': False,
            'output_voltage_pwm_limit': False,
        },
        'MotorErrors': {
            'motor_over_speed': False,
            'desaturation_fault': False,
            'rail_15v_uvlo': False,
            'config_read_error': False,
            'watchdog_reset': False,
            'bad_motor_position': False,
            'dc_bus_over_voltage': False,
            'software_over_current': False,
            'hardware_over_current': False,
        },
    
        'mppts': [{
            'Input_Voltage': 50,
            'Input_Current': 45,
            'Output_Voltage': 50,
            'Output_Current': 45,
            'Output_Power': 50 * 45,
            'efficiency': 98,

            'Mosfet_Temperature': 35,
            'MPPT_Temperature': 35,
            'flags': {
                'hw_overvolt': False,
                'hw_overcurrent':  False,
                'under12v': False,
                'low_array_power': False,
                'battery_full': False,
                'battery_low': False,
                'mosfet_overheat': False,
            }
        } for _ in range(4)],

        'CabinSensors': {
            'Cabin_CO_Content': 0.2,
            'Cabin_CH4_Content': 3,
            'Cabin_NH3_Content': 4,
            'Cabin_NO2_Content': 5,
            'Cabin_O2_Content': 6,
            'Cabin_Temperature': 35,
            'Cabin_Pressure': 76,
            'Cabin_CO2_Content': 2,
        }
    },
    "historic": {
        'Timestamps': [],
        'Speed': [],
        'Battery': [],
        'Power': [],
        'Solar': [],
        'Bus_Power': [],
        'Motor_Velocity': [],
        'Speed2': [],
        'PhaseA_Current': [],
        'solar_input_voltage': [],
        'solar_output_power': [],
        'Acceleration': [],
        'Altitude': [],
    }
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

async def update_processor(queue: asyncio.Queue):
    """Background task that waits for data update events and broadcasts"""
    try:
        count = 0
        while True:
            (ptype, pdata) = await queue.get()
            # await asyncio.sleep(1)

            update_packet = {"type": "update"}
            metric = current_data['metric']
            # ptype = 'None'
            # count += 1
            # metric['Speed'] = count % 10

            # if(count > 10):
            #     metric['bmsFlags']['cell_over_voltage'] = True
            # print( ptype, pdata)

            if ptype == "A":
                # Direct data
                for k in PACKET_A_DIRECT_KEYS:
                    metric[k] = pdata[k]
                
                # Direct data - reorganised
                mppts = []
                solar_o = 0
                solar_i_v = 0
                for i, old in zip(MPPT_NAMES, current_data['metric']['mppts']):
                    d = {k: pdata[k + f"_{i}"]
                        for k in MPPT_VALUE_KEYS}
                    
                    d['Output_Power'] = ds_o = d['Output_Voltage'] * d['Output_Current']
                    # d['Output_Power'] = ds_o = d['Input_Voltage'] * d['Input_Current']
                    solar_o +=  ds_o
                    solar_i_v += d['Input_Voltage']
            
                    d['efficiency'] = 100 * ds_o / max(d['Input_Voltage'] * d['Input_Current'], 0.00001)
                    d['efficiency'] = max(0, d['efficiency'])

                    d['Mosfet_Temperature'] = old['Mosfet_Temperature']
                    d['MPPT_Temperature'] = old['MPPT_Temperature']

                    d['flags'] = {
                        key: pdata[F"MPPT_{i}_Flag{j+1}"]
                        for j, key in enumerate(MPPT_FLAG_NAMES) if key
                    }
                    mppts.append(d)
                
                metric['mppts'] = mppts
                solar_i_v /= 4

                # Flags
                metric['precharge_state'] = sum(i * pdata[f'Precharge_State_Flag{i}'] for i in range(1, 6))
                metric['contactor_flags'] = {
                    key: pdata[f"Precharge_Contactor_Flag{j+1}"]
                    for j, key in enumerate(CONTACTOR_FLAG_NAMRS) if key
                }
                metric['bmsFlags'] = {
                    key: pdata[f"BMS_Flag{j+1}"]
                    for j, key in enumerate(BMS_FLAG_NAMES) if key
                }
                metric['MotorLimits'] = {
                    key: pdata[f"MC_Limit_Flag{j+1}"]
                    for j, key in enumerate(MOTOR_LIMIT_NAMES) if key          
                }
                metric['MotorErrors'] = {
                    key: pdata[f"MC_Error_Flag{j+1}"]
                    for j, key in enumerate(MOTOR_ERROR_NAMES) if key          
                }

                # Derived data
                metric['PhaseA_Current'] = phase_a_current = (metric['PhaseB_Current'] + metric['PhaseB_Current']) / 2.0
                metric['power_consumption'] = output_power = pdata['Pack_Voltage'] * pdata['Pack_Current']
                metric['Bus_Power'] = b_output_power = pdata['Bus_Voltage'] * pdata['Bus_Current']
                metric['Speed2'] = pdata['Vehicle_Velocity']
                metric['solar_input'] = solar_o

                historic = {
                    'Timestamps': pdata['Timestamp'],
                    'Speed': pdata['Speed'],
                    'Battery': pdata['SOC_Ah'],
                    'Power': output_power,
                    'Solar': solar_o,
                    'Bus_Power': b_output_power,
                    'Motor_Velocity': pdata['Motor_Velocity'],
                    'Speed2': pdata['Vehicle_Velocity'],

                    'PhaseA_Current': phase_a_current,

                    'solar_input_voltage': solar_i_v,
                    'solar_output_power': solar_o,

                    'Altitude': pdata['Altitude'],
                    'Acceleration': math.sqrt(sum(pdata[f'acc_{i}']**2 for i in ('X', 'Y', 'Z'))),
                }

                for k in current_data['historic']:
                    if k in historic:
                        current_data['historic'][k].append(historic[k])

                update_packet['historic'] = historic
            
            if ptype == 'B':
                for k in PACKET_B_DIRECT_KEYS:
                    metric[k] = pdata[k]
                
                mppts = []
                for i, old in zip(MPPT_NAMES, current_data['metric']['mppts']):
                    mppts.append({
                        **old,
                        'Mosfet_Temperature': pdata[f'Mosfet_Temp_{i}'],
                        'MPPT_Temperature': min(pdata[f'Controller_Temp_{i}'], 100),
                    })
                metric['mppts'] = mppts
                
                metric['cmus'] = []
                output_power = 0
                
                # minTemp, maxTemp = float('inf'), -float('inf')
                # minVolt, maxVolt = float('inf'), -float('inf')
                
                minTemp, maxTemp = 100, -100
                minVolt, maxVolt = 100, -100

                for i in range(1, 6):
                    d = {
                        "temperature": pdata[f"CMU{i}_Temp"],
                        "cell_temperature": pdata[f"Cell{i}_Temp"],
                    }
                    minTemp = min(minTemp, d['temperature'], d['cell_temperature'])
                    maxTemp = max(maxTemp, d['temperature'], d['cell_temperature'])

                    d['cell_voltages'] = [pdata[f"CMU{i}_Cell{j}_Voltage"] for j in range(8)]
                    minVolt = min(minVolt, min(d['cell_voltages']))
                    maxVolt = max(maxVolt, max(d['cell_voltages']))

                    metric['cmus'].append(d)

                metric['battery_ranges'] = {
                    'min_temp': minTemp,
                    'max_temp': maxTemp,
                    'min_volt': minVolt,
                    'max_volt': maxVolt,
                }

                metric['CabinSensors'] = {
                    key: pdata[key]
                    for key in CABIN_FLAG_NAMES       
                }
                
            current_data['metric'] = update_packet['metric'] = metric

            # Broadcast update =====================================
            print("broadcasting")
            await manager.broadcast(json.dumps(update_packet, default=lambda o: "Infinity" if o == float('inf') 
                  else "-Infinity" if o == float('-inf') 
                  else "NaN" if o != o  # NaN check
                  else None))
            # pprint(update_packet)
    
    except Exception as e:
        print(f"PRocessor crashed: {e}")
        traceback.print_exc()
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data and start background tasks"""
    
    queue = asyncio.Queue()

    # Store the event loop for cross-thread communication
    loop = asyncio.get_event_loop()
    t1 = asyncio.create_task(update_processor(queue))

    thread =  threading.Thread(
        target=run_downlink,
        args=(queue, loop),
        daemon=True
    )
    thread.start()

    yield

    t1.cancel()

    # Cancel thread somehow
    return

app = FastAPI(title="Telemetry Dashboard API", lifespan=lifespan)

# Enable CORS for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your Svelte dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Telemetry Dashboard API", "docs": "/docs"}

# API Routes
@app.get("/api/data/historical")
async def get_historical_data():
    """Get all cached historical data for initial dashboard load"""
    return {
        'metric': current_data["metric"],
        'historic': current_data["historic"]
    }

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial data to new client
        data = {
            'type': 'data',
            'metric': current_data["metric"],
            "historic": current_data["historic"]
        }
        await websocket.send_text(json.dumps(data))
        
        # Keep connection alive and wait for disconnect
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
