<script lang="ts">
    import {globalStore} from "$lib/store";
    import type { TelemetryData } from "$lib/store_types";

    // Utility functions
    function formatValue(value: number | undefined, unit: string = "", decimals: number = 2): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function getVoltageStatusColor(voltage: number | undefined): string {
        if (typeof voltage !== "number") return "bg-gray-600";

        // const [min, max] = [2.5, 4.2];
        if (voltage > 4.2 || voltage < 2.5) return "bg-red-500";
        if (voltage > 2.5 && voltage < 2.8) return "bg-yellow-500";
        return "bg-green-500";
    }

    function getTemperatureStatusColor(temperature: number | undefined): string {
        if (typeof temperature !== "number") return "bg-gray-600";

        if (temperature > 45) return "bg-red-500";
        if (temperature > 35) return "bg-yellow-500";
        return "bg-green-500";
    }

    function getVoltageProgressWidth(voltage: number | undefined): number {
        if (typeof voltage !== "number") return 0;
        return Math.min(100, Math.max(0, ((voltage - 2.5) / (4.2 - 2.5)) * 100));
    }

    // New utility functions for precharge and contactor states
    function getPrechargeStateInfo(state: number) {
        const states = [
            { name: "Error", color: "bg-red-500", textColor: "text-red-400" },
            { name: "Idle", color: "bg-gray-500", textColor: "text-gray-400" },
            { name: "Measure", color: "bg-blue-500", textColor: "text-blue-400" },
            { name: "Pre-charge", color: "bg-yellow-500", textColor: "text-yellow-400" },
            { name: "Run", color: "bg-green-500", textColor: "text-green-400" },
            { name: "Enable Pack", color: "bg-cyan-500", textColor: "text-cyan-400" }
        ];
        return states[state] || states[0];
    }

    function getContactorStateColor(isError: boolean, isOn: boolean): string {
        if (isError) return "bg-red-500";
        return isOn ? "bg-green-500" : "bg-gray-500";
    }

    interface ContactorFlag {
        [key: `error${number}`]: boolean;
        [key: `output${number}`]: boolean;
        supply: boolean;
    };
    interface bmsFlag {
        key: keyof TelemetryData['metric']['bmsFlags'];
        label: string;
        color?: string;
    };



    const bmsLabels: bmsFlag[] = [
        { key: 'cell_over_voltage', label: 'CellOverVolt' },
        { key: 'cell_under_voltage', label: 'CellUnderVolt' },
        { key: 'cell_over_temp', label: 'CellOverTemp' },
        { key: 'measurement_untrusted', label: 'MeasErr' },
        { key: 'measurement_untrusted', label: 'CMU_TO' },
        { key: 'vehicle_comm_timeout', label: 'Veh_TO' },
        { key: 'bms_setup_mode', label: 'Setup' },
        { key: 'cmu_can_status', label: 'CAN_Status', color: 'bg-green-400'},
        { key: 'isolation_test_fail', label: 'IsolationFail' },
        { key: 'soc_invalid', label: 'SoC_Invalid' },
        { key: 'can_supply_low', label: 'CAN_Low' },
        { key: 'contactor_not_engaged', label: 'Cont_NE' },
        { key: 'extra_cell_detected', label: 'Extra_Cell' }
    ];
</script>

<div class="space-y-6 p-6">
    <!-- Main Battery Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="metric-card col-span-1 md:col-span-2">
            <div class="metric-value text-green-400 text-3xl">
                {formatValue($globalStore.metric.SOC_Ah, "Ah", 0)}
            </div>
            <div class="metric-label">State of Charge</div>
            <div class="mt-2 bg-gray-700 rounded-full h-2">
                <div
                    class="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style="width: {80}%"
                    ></div>
                    <!-- style="width: {battery.state_of_charge || 0}%" -->
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue($globalStore.metric.Pack_Voltage, "V")}
            </div>
            <div class="metric-label">Pack Voltage</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-blue-400">
                {formatValue($globalStore.metric.Pack_Current, "A")}
            </div>
            <div class="metric-label">Pack Current</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue($globalStore.metric.battery_ranges.max_temp, "°C")}
            </div>
            <div class="metric-label">Max Temperature</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value text-cyan-400">
                {formatValue($globalStore.metric.battery_ranges.min_temp, "°C")}
            </div>
            <div class="metric-label">Min Temperature</div>
        </div>
    </div>

    <!-- Status Indicators -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Voltage Range</span>
                <span class="text-sm text-gray-300">
                    {formatValue($globalStore.metric.battery_ranges.min_volt, "V")} - {formatValue(
                        $globalStore.metric.battery_ranges.max_volt,
                        "V"
                    )}
                </span>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Temperature Range</span>
                <span class="text-sm text-gray-300">
                    {formatValue($globalStore.metric.battery_ranges.min_temp, "°C")} - {formatValue(
                        $globalStore.metric.battery_ranges.max_temp,
                        "°C"
                    )}
                </span>
            </div>
        </div>

        <!-- Enhanced Pre-charge State -->
        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Pre-charge State</span>
                <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full {getPrechargeStateInfo($globalStore.metric.precharge_state).color}"></div>
                    <span class="text-sm {getPrechargeStateInfo($globalStore.metric.precharge_state).textColor}">
                        {getPrechargeStateInfo($globalStore.metric.precharge_state).name}
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- Compact Contactor Status -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between">
            <div class="flex items-center justify-start flex-1 space-x-6">
                <span class="text-sm text-gray-400">Contactors:</span>
                {#each [1, 2, 3] as contactorNum}
                    {@const isError = $globalStore.metric.contactor_flags[`contactor${contactorNum}_error`]}
                    {@const isOn = $globalStore.metric.contactor_flags[`contactor${contactorNum}_output`]}
                    <div class="flex items-center space-x-3">
                        <span class="text-sm text-gray-300">C{contactorNum}</span>
                        <div class="flex items-center space-x-1">
                            <span class="text-sm text-gray-400">O:</span>
                            <div class="w-3 h-3 rounded-full {isOn ? 'bg-green-500' : 'bg-gray-500'}"></div>
                        </div>
                        <div class="flex items-center space-x-1">
                            <span class="text-sm text-gray-400">E:</span>
                            <div class="w-3 h-3 rounded-full {isError ? 'bg-red-500' : 'bg-green-500'}"></div>
                        </div>
                        {#if contactorNum < 3}
                            <div class="w-px h-4 bg-gray-600"></div>
                        {/if}
                    </div>
                {/each}
            </div>
            <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-400">Supply:</span>
                <div class="w-3 h-3 rounded-full {$globalStore.metric.contactor_flags.contactor_supply ? 'bg-green-500' : 'bg-red-500'}"></div>
            </div>
        </div>
    </div>

    <!-- BMS Status Flags -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-gray-400">BMS Status:</span>
        </div>
        <div class="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-7 gap-4">
            {#each bmsLabels as flag}
                {@const isActive = $globalStore.metric.bmsFlags[flag.key]}
                <div class="flex items-center justify-center space-x-1">
                    <div class="w-3 h-3 rounded-full {isActive ? `${flag['color'] || 'bg-red-500'}` : 'bg-gray-500'} flex-shrink-0"></div>
                    <span class="text-xs text-gray-300">{flag.label}</span>
                </div>
            {/each}
        </div>
    </div>

    <!-- Battery Packs List View -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div class="mb-4">
            <h3 class="text-lg font-semibold">Battery Pack Details</h3>
        </div>

        <div class="space-y-4">
            {#each $globalStore.metric.cmus as cmu, cmuIndex}
                <div class="bg-gray-700 rounded-lg p-4 border border-gray-600">
                    <!-- Pack Header -->
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-4">
                            <h4 class="text-lg font-medium text-white">
                                CMU {cmuIndex + 1}
                            </h4>
                            <div class="flex items-center space-x-4">
                                <!-- CMU Temperature -->
                                <div class="flex items-center space-x-2">
                                    <div
                                        class="w-3 h-3 rounded-full {getTemperatureStatusColor(cmu.temperature)}"
                                    ></div>
                                    <span class="text-sm text-gray-300">
                                        CMU: {formatValue(cmu.temperature, "°C", 1)}
                                    </span>
                                </div>
                                <!-- Cell Temperature -->
                                <div class="flex items-center space-x-2">
                                    <div
                                        class="w-3 h-3 rounded-full {getTemperatureStatusColor(cmu.cell_temperature)}"
                                    ></div>
                                    <span class="text-sm text-gray-300">
                                        Cell: {formatValue(cmu.cell_temperature, "°C", 1)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Cell Grid -->
                    {#if cmu.cell_voltages && cmu.cell_voltages.length > 0}
                        <div class="grid grid-cols-8 gap-3">
                            {#each cmu.cell_voltages as cellv, cellIndex}
                                <div class="bg-gray-600 rounded p-3 text-center">
                                    <div class="text-xs text-gray-400 mb-1">
                                        Cell {cellIndex}
                                    </div>
                                    <div class="text-sm font-medium mb-2">
                                        {formatValue(cellv, "V", 3)}
                                    </div>
                                    <div class="w-full h-2 rounded-full bg-gray-500">
                                        <div
                                            class="h-2 rounded-full {getVoltageStatusColor(
                                                cellv,
                                            )}"
                                            style="width: {getVoltageProgressWidth(cellv)}%"
                                        ></div>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <div class="text-center text-gray-400 py-4">
                            No cell data available for Pack {cmuIndex + 1}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>

        <!-- Legend -->
        <div class="mt-4 flex justify-center space-x-6 text-xs">
            <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded"></div>
                <span>Normal</span>
            </div>
            <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>Warning</span>
            </div>
            <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-red-500 rounded"></div>
                <span>Critical</span>
            </div>
        </div>
    </div>
</div>

<style lang='postcss'>
    @reference "tailwindcss";

    .metric-card {
        @apply bg-gray-800 rounded-lg p-4 border border-gray-700;
    }

    .metric-value {
        @apply text-2xl font-bold mb-1;
    }

    .metric-label {
        @apply text-sm text-gray-400;
    }
</style>