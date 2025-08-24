export interface BatteryPackData {
    temperature: number;
    cell_temperature: number;
    cell_voltages: number[];
}

export interface BatteryRangeData {
    min_temp: number;
    max_temp: number;
    min_volt: number;
    max_volt: number;
}

export interface CabinSensors {
    Cabin_CO_Content: number;
    Cabin_CH4_Content: number;
    Cabin_NH3_Content: number;
    Cabin_NO2_Content: number;
    Cabin_O2_Content: number;
    Cabin_Temperature: number;
    Cabin_Pressure: number;
    Cabin_CO2_Content: number;
}

export interface MPPTFlags {
    [key: string]: boolean;
    hw_overvolt:  boolean;
    hw_overcurrent:  boolean;
    under12v:  boolean;
    low_array_power: boolean;
    battery_full:  boolean;
    battery_low:  boolean;
    mosfet_overheat: boolean;
}

export interface MPPTData {
    Input_Voltage: number;
    Input_Current: number;
    Output_Voltage: number;
    Output_Current: number;
    Output_Power: number;
    efficiency: number;

    Mosfet_Temperature: number;
    MPPT_Temperature: number;

    flags: MPPTFlags;
}

export interface TelemetryData {
    metric: {
        // Overview
        Pack_Voltage: number;
        SOC_Ah: number;
        power_consumption: number;
        solar_input: number;
        distance_travelled: number;
        Motor_Temp: number;

        // Speed
        Speed: number;
        predicted: number;
        // margin: number;
        // status: "ok" | "error";

        // Battery
        // Pack_Voltage: number;
        Pack_Current: number;
        cmus: BatteryPackData[];
        battery_ranges: BatteryRangeData;
        precharge_state: number;
        contactor_flags: {
            [key: string]: boolean;
            [key: `contactor${number}_error`]: boolean;
            [key: `contactor${number}_output`]: boolean;
            contactor_supply: boolean;
        };
        bmsFlags: {
            [key: string]: boolean;
            cell_over_voltage: boolean;
            cell_under_voltage: boolean;
            cell_over_temp: boolean;
            measurement_untrusted: boolean;
            cmu_comm_timeout: boolean;
            vehicle_comm_timeout: boolean;
            bms_setup_mode: boolean;
            cmu_can_status: boolean;
            isolation_test_fail: boolean;
            soc_invalid: boolean;
            can_supply_low: boolean;
            contactor_not_engaged: boolean;
            extra_cell_detected: boolean;
        };

        // Motor
        Motor_Velocity: number;
        Speed2: number;
        HeatSink_Temp: number;
        PhaseA_Current: number;
        PhaseB_Current: number;
        PhaseC_Current: number;
        Bus_Voltage: number;
        Bus_Current: number;
        Bus_Power: number;
        DSP_Board_Temp: number;

        MotorLimits: {
            [key: string]: boolean;
            ipm_temp_limit: boolean;
            bus_voltage_lower_limit: boolean;
            bus_voltage_upper_limit: boolean;
            bus_current_limit: boolean;
            velocity_limit: boolean;
            motor_current_limit: boolean;
            output_voltage_pwm_limit: boolean;
        };

        MotorErrors: {
            [key: string]: boolean;
            motor_over_speed: boolean;
            desaturation_fault: boolean;
            rail_15v_uvlo: boolean;
            config_read_error: boolean;
            watchdog_reset: boolean;
            bad_motor_position: boolean;
            dc_bus_over_voltage: boolean;
            software_over_current: boolean;
            hardware_over_current: boolean;
        };

        // Solar
        mppts: MPPTData[];

        // cabin sensors
        CabinSensors: CabinSensors;
    };

    historic: {
        Timestamps: string[];
        Speed: number[];
        Battery: number[];
        Power: number[];
        Solar: number[];

        // Motor
        // timestamps_motor: [];
        Bus_Power: number[];
        Motor_Velocity: number[];
        Speed2: number[];

        PhaseA_Current: number[];

        // Solar
        solar_input_voltage: number[];
        solar_output_power: number[];

        // Strategy
        Acceleration: number[];
        Altitude: number[];
        Latitudes: number[];
        Longitudes: number[];
    };
}

export interface UpdatePacket {
    type: "update"
    metric: TelemetryData["metric"];

    historic: {
        Timestamps: string;
        Speed: number;
        Battery: number;
        Power: number;
        Solar: number;

        Bus_Power: number;
        Motor_Velocity: number;
        Speed2: number;

        solar_input_voltage: number,
        solar_output_power: number,
        PhaseA_Current: number,

        Acceleration: number,
        Altitude: number,
        Latitudes: number;
        Longitudes: number;
    };
}

export interface DataPacket {
    type: "data";
    metric: TelemetryData["metric"];
    historic: TelemetryData["historic"];
}