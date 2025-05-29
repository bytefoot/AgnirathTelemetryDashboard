from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
import uvicorn
from contextlib import asynccontextmanager

# Global state to store current data
current_data = {
    "metric": {
        'pack_voltage': 48.2,
        'battery_level': 87.0,
        'power_consumption': 1250.0,
        'solar_input': 450.0,
        'distance_travelled': 142.8,
        'motor_temperature': 68.5,
        'speed': 65.4,
        'predicted': 67.2,

        'soc': 12000,
        'pack_current': 46.26,
        'cmus': [{'temperature': 30.12, 'cell_voltages': [3.7 for _ in range(8)]} for _ in range(5)]
    },
    "historic": {
        'timestamps': [],
        'speed': [],
        'battery': [],
        'power': [],
        'solar': []
    }
}

update_packet = {
    'type': 'update',
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

def generate_historical_data():
    """Generate initial historical data for the past hour"""
    now = datetime.now()
    timestamps = []
    speed_data = []
    battery_data = []
    power_data = []
    solar_data = []

    for i in range(59, -1, -1):  # 60 points, going backwards
        time_point = now - timedelta(seconds=i)
        timestamps.append(time_point.strftime("%H:%M:%S"))
        
        # Generate realistic telemetry data
        speed_data.append(60 + math.sin(i / 10) * 15 + random.uniform(-2.5, 2.5))
        battery_data.append(max(20, 90 - i * 0.8 + random.uniform(-1.5, 1.5)))
        power_data.append(1000 + math.sin(i / 8) * 400 + random.uniform(-50, 50))
        solar_data.append(max(0, 400 + math.sin(i / 12) * 200 + random.uniform(-25, 25)))

    current_data["historic"] = {
        'timestamps': timestamps,
        'speed': speed_data,
        'battery': battery_data,
        'power': power_data,
        'solar': solar_data
    }

# Event-driven data update system
data_update_event = asyncio.Event()

async def broadcast_data_update():
    """Broadcast current data to all WebSocket clients when triggered"""
    # data = {
    #     'metric': current_data["metric"],
    #     "history": current_data["history"]
    # }
    print("broadcasting")
    await manager.broadcast(json.dumps(update_packet))

def trigger_data_broadcast():
    """Trigger a broadcast - call this when new serial data arrives"""
    if hasattr(trigger_data_broadcast, '_loop'):
        loop = trigger_data_broadcast._loop
        if loop.is_running():
            # This ensures the event gets set in the correct event loop
            loop.call_soon_threadsafe(data_update_event.set)

async def background_broadcaster():
    """Background task that waits for data update events and broadcasts"""
    while True:
        await data_update_event.wait()  # Wait for data update signal
        try:
            await broadcast_data_update()
        finally:
            data_update_event.clear()  # Reset the event AFTER broadcasting

# Serial data processing functions
def update_telemetry_from_serial(serial_data: dict):
    """Update telemetry data from serial input and trigger broadcast"""
    try:
        current_data['metric'].update(serial_data['metric'])
        
        for k in current_data['historic']:
            if k in serial_data['historic']:
                current_data['historic'][k].append(serial_data['historic'][k])

        update_packet.update(serial_data)
        # Trigger broadcast to all WebSocket clients
        # data_update_event.set()``
        trigger_data_broadcast()
        
    except Exception as e:
        print(f"Error updating telemetry from serial: {e}")

# Demo function to simulate serial data updates (remove in production)
async def simulate_serial_updates():
    """Simulate serial data updates - remove this in production"""
    while True:
        await asyncio.sleep(1)  # Wait 5 seconds between updates
        # Simulate receiving serial data
        simulated_serial_data = {
            'metric': {
                'pack_voltage': 48.2 + random.uniform(-0.5, 0.5),
                'battery_level': max(0, current_data['metric']['battery_level'] - random.uniform(0.05, 0.15)),
                'power_consumption': 1250 + random.uniform(-100, 100),
                'solar_input': max(0, 450 + random.uniform(-50, 50)),
                'distance_travelled': current_data["metric"]['distance_travelled'] + random.uniform(0.08, 0.12),
                'motor_temperature': 68.5 + random.uniform(-2, 2),
                'speed': 65 + random.uniform(-5, 5),
                'predicted': 67 + random.uniform(-3, 3),

                'soc': 12000 + random.uniform(-3, 3),
                'pack_current': 46 + random.gauss(0, 4),
                'cmus': [{'temperature': 30 + random.gauss(0, 1.5), 'cell_voltages': [3.7 + random.gauss(0, 0.45) for _ in range(8)]} for _ in range(5)]
            },
            'historic': {
                'timestamps': datetime.now().strftime("%H:%M:%S"),
                'speed': 60 + math.sin(time.time() / 100) * 15 + random.uniform(-2.5, 2.5),
                'battery': max(0, current_data["historic"]['battery'][-1] - 2) if current_data["historic"]['battery'] else 85,
                'power': 1000 + math.sin(time.time() / 80) * 400 + random.uniform(-50, 50),
                'solar': max(0, 400 + math.sin(time.time() / 120) * 200 + random.uniform(-25, 25))
            }
        }

        update_telemetry_from_serial(simulated_serial_data)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data and start background tasks"""
    generate_historical_data()
    # Store the event loop for cross-thread communication
    trigger_data_broadcast._loop = asyncio.get_event_loop()
    # Start the background broadcaster task
    t1 = asyncio.create_task(background_broadcaster())
    # Start demo serial simulation (remove in production)
    t2 = asyncio.create_task(simulate_serial_updates())

    app.state.background_tasks = set()
    app.state.background_tasks.add(t1)
    app.state.background_tasks.add(t2)

    t1.add_done_callback(app.state.background_tasks.discard)
    t2.add_done_callback(app.state.background_tasks.discard)

    yield

    for task in app.state.background_tasks:
        task.cancel()
    await asyncio.gather(*app.state.background_tasks, return_exceptions=True)

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