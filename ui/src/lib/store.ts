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
            cell_temperature: 0,
            cell_voltages: Array.from({ length: 8 }, () => 0)
        })),
        battery_ranges: {
            min_temp: 0,
            max_temp: 0,
            min_volt: 0,
            max_volt: 0,
        },
        precharge_state: 0,
        contactor_flags: {
            contactor1_error: false,
            contactor2_error: false,
            contactor3_error: false,
            contactor1_output: false,
            contactor2_output: false,
            contactor3_output: false,

            contactor_supply: false,
        },
        bmsFlags: {
            cell_over_voltage: false,
            cell_under_voltage: false,
            cell_over_temp: false,
            measurement_untrusted: false,
            cmu_comm_timeout: false,
            vehicle_comm_timeout: false,
            bms_setup_mode: false,
            cmu_can_status: false,
            isolation_test_fail: false,
            soc_invalid: false,
            can_supply_low: false,
            contactor_not_engaged: false,
            extra_cell_detected: false,
        },

        // Motor
        Motor_Velocity: 0,
        Speed2: 0,
        HeatSink_Temp: 0,
        PhaseA_Current: 0,
        PhaseB_Current: 0,
        PhaseC_Current: 0,
        Bus_Voltage: 0,
        Bus_Current: 0,
        Bus_Power: 0,
        DSP_Board_Temp: 0,
        MotorLimits: {
            ipm_temp_limit: false,
            bus_voltage_lower_limit: false,
            bus_voltage_upper_limit: false,
            bus_current_limit: false,
            velocity_limit: false,
            motor_current_limit: false,
            output_voltage_pwm_limit: false,
        },
        MotorErrors: {
            motor_over_speed: false,
            desaturation_fault: false,
            rail_15v_uvlo: false,
            config_read_error: false,
            watchdog_reset: false,
            bad_motor_position: false,
            dc_bus_over_voltage: false,
            software_over_current: false,
            hardware_over_current: false,
        },

        // Solar
        mppts: Array.from({ length: 4 }, () => ({
            Input_Voltage: 0,
            Input_Current: 0,
            Output_Voltage: 0,
            Output_Current: 0,
            Output_Power: 0,
            efficiency: 0,

            Mosfet_Temperature: 0,
            MPPT_Temperature: 0,

            flags: {
                hw_overvolt: false,
                hw_overcurrent:  false,
                under12v: false,
                low_array_power: false,
                battery_full: false,
                battery_low: false,
                mosfet_overheat: false,
            }
        })),

        CabinSensors: {
            Cabin_CO_Content: 0,
            Cabin_CH4_Content: 0,
            Cabin_NH3_Content: 0,
            Cabin_NO2_Content: 0,
            Cabin_O2_Content: 0,
            Cabin_Temperature: 0,
            Cabin_Pressure: 0,
            Cabin_CO2_Content: 0,
        }
    },
    historic: {
        Timestamps: [],
        Speed: [],
        Battery: [],
        Power: [],
        Solar: [],

        PhaseA_Current: [],

        // Motor
        // timestamps_motor: [];
        Bus_Power: [],
        Motor_Velocity: [],
        Speed2: [],
        
        // Solar
        solar_input_voltage: [],
        solar_output_power: [],

        // Strategy
        Acceleration: [],
        Altitude: [],
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