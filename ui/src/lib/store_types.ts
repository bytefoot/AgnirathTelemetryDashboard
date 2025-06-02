export interface BatteryPackData {
    temperature: number;
    cell_voltages: number[];
}

export interface MPPTData {
    Input_Voltage: number;
    Input_Current: number;
    Output_Voltage: number;
    Output_Current: number;
    Output_Power: number;
    efficiency: number;
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

        // Pack_Voltage: number;
        Pack_Current: number;
        cmus: BatteryPackData[];

        // Motor
        Motor_Velocity: number;
        Speed2: number;
        HeatSink_Temp: number;
        PhaseB_Current: number;
        PhaseC_Current: number;
        Bus_Voltage: number;
        Bus_Current: number;
        Bus_Power: number;

        // Solar
        mppts: MPPTData[];
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

        // Solar
        solar_input_voltage: number[],
        solar_output_power: number[],
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
    };
}

export interface DataPacket {
    type: "data";
    metric: TelemetryData["metric"];
    historic: TelemetryData["historic"];
}