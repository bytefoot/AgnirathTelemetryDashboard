export interface BatteryPackData {
    temperature: number;
    cell_voltages: number[];
}

export interface TelemetryData {
    metric: {
        // Overview
        pack_voltage: number;
        battery_level: number;
        power_consumption: number;
        solar_input: number;
        distance_travelled: number;
        motor_temperature: number;

        // Speed
        speed: number;
        predicted: number;
        // margin: number;
        // status: "ok" | "error";

        // Battery
        soc: number;
        // pack_voltage: number;
        pack_current: number;
        cmus: BatteryPackData[];
    };

    historic: {
        timestamps: string[];
        speed: number[];
        battery: number[];
        power: number[];
        solar: number[];
    };
}

export interface UpdatePacket {
    type: "update"
    metric: TelemetryData["metric"];

    historic: {
        timestamps: string;
        speed: number;
        battery: number;
        power: number;
        solar: number;
    };
}

export interface DataPacket {
    type: "data";
    metric: TelemetryData["metric"];
    historic: TelemetryData["historic"];
}