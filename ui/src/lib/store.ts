import { writable } from 'svelte/store';
import type {DataPacket, TelemetryData, UpdatePacket, BatteryPackData} from "$lib/store_types.ts"

// Initial state
const initialState: TelemetryData = {
    metric: {
        // Overview
        Pack_Voltage: 0,
        SOC_Ah: 0,
        power_consumption: 0,
        solar_input: 0,
        distance_travelled: 0,
        Motor_Temp: 0,

        // Speed
        Speed: 0,
        predicted: 0,

        // Battery
        Pack_Current: 0,
        cmus: Array.from({ length: 5 }, () => ({
            temperature: 0,
            cell_voltages: Array.from({ length: 8 }, () => 0)
        })),

        // Motor
        Motor_Velocity: 0,
        Speed2: 0,
        HeatSink_Temp: 0,
        PhaseB_Current: 0,
        PhaseC_Current: 0,
        Bus_Voltage: 0,
        Bus_Current: 0,
        Bus_Power: 0,

        // Solar
        mppts: Array.from({ length: 4 }, () => ({
            Input_Voltage: 0,
            Input_Current: 0,
            Output_Voltage: 0,
            Output_Current: 0,
            Output_Power: 0,
            efficiency: 0,
        })),
    },
    historic: {
        Timestamps: [],
        Speed: [],
        Battery: [],
        Power: [],
        Solar: [],

        // Motor
        // timestamps_motor: [];
        Bus_Power: [],
        Motor_Velocity: [],
        Speed2: [],
        
        // Solar
        solar_input_voltage: [],
        solar_output_power: [],
    }
};

// Create the store with type-safe methods
function createStore() {
    const { subscribe, set, update } = writable<TelemetryData>(initialState);

    return {
        subscribe,
        // Update a single value
        updateValue: <K extends keyof TelemetryData['metric']>(
            key: K, 
            value: TelemetryData['metric'][K]
        ) => update(state => {
            state.metric[key] = value;
            return state;
        }),
        // Append to an array
        appendToArray: <K extends keyof TelemetryData['historic']>(
            key: K,
            items: TelemetryData['historic'][K] extends Array<infer T> ? T[] : never
        ) => update(state => {
            const current = state.historic[key];
            if (!Array.isArray(current)) {
                console.error(`Key ${String(key)} is not an array`);
                return state;
            }
            state.historic[key] = [...current, ...items] as TelemetryData['historic'][K];
            return state;
        }),
    
        reset: () => set(initialState),

        handleWebSocketUpdate: (message: UpdatePacket) => {
            try {
                update(state => {
                    const newState = { ...state };
        
                    if (message.metric) {
                        // Type-safe iteration
                        (Object.keys(message.metric) as Array<keyof TelemetryData['metric']>).forEach(key => {
                            if (message.metric && key in newState.metric) {
                                newState.metric[key] = (message.metric[key]! as any);
                            }
                        });
                    }
                    if (message.historic) {
                        // Type-safe iteration
                        (Object.keys(message.historic) as Array<keyof TelemetryData['historic']>).forEach(key => {
                            if (message.historic && key in state.historic) {
                                newState.historic[key] = [
                                    ...newState.historic[key],  // Keep existing values
                                    (message.historic[key] as any)  // Add new values
                                ];
                    
                                const MAX_HISTORY = 1000;
                                if (newState.historic[key].length > MAX_HISTORY) {
                                    newState.historic[key] = (newState.historic[key].slice(-MAX_HISTORY) as (string[] & number[]));
                                }
                            }
                        });
                    }
                    return newState;
                });
            } catch (e) {
                console.error('Error processing WebSocket message:', e);
            }
        },

        handleWebSocketData: (message: DataPacket) => {
            try {
                update((state) => {
                    // Create a new state object to avoid direct mutation
                    const newState = { ...state };
        
                    // Update metric values (single values)
                    if (message.metric) {
                        const metricKeys = Object.keys(message.metric) as Array<keyof typeof message.metric>;
                        metricKeys.forEach((key) => {
                            if (key in newState.metric && message.metric[key] !== undefined) {
                                newState.metric[key] = message.metric[key] as any;
                            }
                        });
                    }
        
                    // Update historic data (arrays)
                    if (message.historic) {
                        const historicKeys = Object.keys(message.historic) as Array<keyof typeof message.historic>;
                        historicKeys.forEach((key) => {
                            if (key in newState.historic && message.historic[key]) {
                                newState.historic[key] = [...(message.historic[key] as any[])!];
                            }
                        });
                    }
        
                    return newState;
                });
            } catch (e) {
                console.error('Error processing WebSocket message:', e);
            }
        },
    };

}

export const globalStore = createStore();