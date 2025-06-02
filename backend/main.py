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

from downlink import main as run_downlink

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
        'cmus': [{'temperature': 30.12, 'cell_voltages': [3.7 for _ in range(8)]} for _ in range(5)],

        'Motor_Velocity': 123,
        'Speed2': 75,
        'HeatSink_Temp': 31,
        'PhaseB_Current': 45.6,
        'PhaseC_Current': 45.7,
        'Bus_Voltage': 50,
        'Bus_Current': 45,
        'Bus_Power': 50 * 45,

        'mppts': [{
            'Input_Voltage': 50,
            'Input_Current': 45,
            'Output_Voltage': 50,
            'Output_Current': 45,
            'Output_Power': 50 * 45,
            'efficiency': 98,
        } for _ in range(4)],
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
        'solar_input_voltage': [],
        'solar_output_power': [],
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
        while True:
            (ptype, pdata) = await queue.get()
            # await asyncio.sleep(1)

            # ptype = 'A'
            # pdata = {
            #     "Timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            #     "SOC_Ah": round(random.uniform(0, 200)),  # State of Charge in Ah (0-200Ah range)
            #     "Pack_Voltage": round(random.uniform(300, 800)),  # High voltage battery pack
            #     "Pack_Current": round(random.uniform(-200, 200)),  # Can be negative (charging)
            #     "Bus_Voltage": round(random.uniform(300, 800)),
            #     "Bus_Current": round(random.uniform(-200, 200)),
            #     "Motor_Velocity": round(random.uniform(0, 8000)),  # RPM
            #     "Vehicle_Velocity": round(random.uniform(0, 120)),  # km/h
            #     "PhaseC_Current": round(random.uniform(-150, 150)),
            #     "PhaseB_Current": round(random.uniform(-150, 150)),
            #     "Input_Voltage_A": round(random.uniform(10, 15)),
            #     "Input_Current_A": round(random.uniform(0, 30)),
            #     "Output_Voltage_A": round(random.uniform(10, 15)),
            #     "Output_Current_A": round(random.uniform(0, 30)),
            #     "Input_Voltage_B": round(random.uniform(10, 15)),
            #     "Input_Current_B": round(random.uniform(0, 30)),
            #     "Output_Voltage_B": round(random.uniform(10, 15)),
            #     "Output_Current_B": round(random.uniform(0, 30)),
            #     "Input_Voltage_C": round(random.uniform(10, 15)),
            #     "Input_Current_C": round(random.uniform(0, 30)),
            #     "Output_Voltage_C": round(random.uniform(10, 15)),
            #     "Output_Current_C": round(random.uniform(0, 30)),
            #     "Input_Voltage_D": round(random.uniform(10, 15)),
            #     "Input_Current_D": round(random.uniform(0, 30)),
            #     "Output_Voltage_D": round(random.uniform(10, 15)),
            #     "Output_Current_D": round(random.uniform(0, 30)),
            #     "Latitude": round(random.uniform(-90, 90), 6),
            #     "Longitude": round(random.uniform(-180, 180), 6),
            #     "Altitude": round(random.uniform(-100, 3000)),  # Meters
            #     "Speed": round(random.uniform(0, 120)),  # km/h
            #     "acc_X": round(random.uniform(-2, 2)),  # m/s²
            #     "acc_Y": round(random.uniform(-2, 2)),
            #     "acc_Z": round(random.uniform(-2, 2)),
            #     "Flags": []  # Dictionary of boolean flags
            # }

            update_packet = {"type": "update"}

            if ptype == "A":
                metric = {}

                # Direct data
                for k in ["SOC_Ah", "Pack_Voltage", "Pack_Current", "Bus_Voltage",
                        "Bus_Current", "Motor_Velocity", "PhaseC_Current",
                        "PhaseB_Current", "Speed"]:
                    metric[k] = pdata[k]
                
                # Direct data - reorganised
                metric['mppts'] = []
                solar_o = 0
                solar_i_v = 0
                for i in ['A', 'B', 'C', 'D']:
                    d = {k: pdata[k + f"_{i}"]
                        for k in ["Input_Voltage", f"Input_Current",
                        "Output_Voltage", f"Output_Current"]}
                    
                    d['Output_Power'] = ds_o = d['Output_Voltage'] * d['Output_Current']
                    solar_o +=  ds_o
                    solar_i_v += d['Input_Voltage']
            
                    d['efficiency'] = ds_o / max(d['Input_Voltage'] * d['Input_Current'], 0.00001)
                    metric['mppts'].append(d)
                solar_i_v /= 4

                # Derived data
                metric['power_consumption'] = output_power = pdata['Bus_Voltage'] * pdata['Bus_Current']
                metric['Speed2'] = pdata['Vehicle_Velocity']
                metric['solar_input'] = solar_o

                historic = {
                    'Timestamps': pdata['Timestamp'],
                    'Speed': pdata['Speed'],
                    'Battery': pdata['SOC_Ah'],
                    'Power': output_power,
                    'Solar': solar_o,
                    'Bus_Power': output_power,
                    'Motor_Velocity': pdata['Motor_Velocity'],
                    'Speed2': pdata['Vehicle_Velocity'],

                    'solar_input_voltage': solar_i_v,
                    'solar_output_power': solar_o,
                }

                for k in current_data['historic']:
                    if k in historic:
                        current_data['historic'][k].append(historic[k])

                update_packet['metric'] = metric
                update_packet['historic'] = historic
            
            if ptype == 'B':
                metric = {}

                metric['cmus'] = []
                output_power = 0
                for i in range(1, 6):
                    d = {"temperature": pdata[f"CMU{i}_Temp"]}
                    d['cell_voltages'] = [pdata[f"CMU{i}_Cell{j}_Voltage"] for j in range(8)]
                    metric['cmus'].append(d)
                
                update_packet['metric'] = metric

            # Broadcast update =====================================
            print("broadcasting")
            await manager.broadcast(json.dumps(update_packet))
    
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
