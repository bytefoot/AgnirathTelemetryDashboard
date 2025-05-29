<script lang="ts">
    import {globalStore} from "$lib/store";
    import type {BatteryPackData} from "$lib/store_types";

    // Utility functions
    function formatValue(value: number | undefined, unit: string = "", decimals: number = 2): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function getVoltageStatusColor(voltage: number | undefined, range?: [number, number]): string {
        if (typeof voltage !== "number") return "bg-gray-600";

        const [min, max] = range || [3.0, 4.0];
        const ratio = (voltage - min) / (max - min);
        if (ratio < 0.2 || ratio > 0.9) return "bg-red-500";
        if (ratio < 0.3 || ratio > 0.8) return "bg-yellow-500";
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
        return Math.min(100, Math.max(0, ((voltage - 3.0) / (4.0 - 3.0)) * 100));
    }

    // Uncomment to use real telemetry data instead of dummy data
    // $: data = $telemetryData;
</script>

<div class="space-y-6 p-6">
    <!-- Main Battery Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="metric-card col-span-1 md:col-span-2">
            <div class="metric-value text-green-400 text-3xl">
                {formatValue($globalStore.metric.soc, "Ah", 0)}
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
                {formatValue($globalStore.metric.pack_voltage, "V")}
            </div>
            <div class="metric-label">Pack Voltage</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-blue-400">
                {formatValue($globalStore.metric.pack_current, "A")}
            </div>
            <div class="metric-label">Pack Current</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-red-400">
                <!-- {formatValue(battery.max_temperature, "°C")} -->
                N/A °C
            </div>
            <div class="metric-label">Max Temperature</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value text-cyan-400">
                N/A °C
                <!-- {formatValue(battery.min_temperature, "°C")} -->
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
                    <!-- {formatValue(battery.voltage_range?.[0], "V")} - {formatValue(
                        battery.voltage_range?.[1],
                        "V"
                    )} -->
                    x - y V
                </span>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Temperature Range</span>
                <span class="text-sm text-gray-300">
                    <!-- {formatValue(battery.temperature_range?.[0], "°C")} - {formatValue(
                        battery.temperature_range?.[1],
                        "°C"
                    )} -->
                    x - y °C
                </span>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Pre-charge State</span>
                <div class="flex items-center space-x-2">
                    <div
                        class="w-3 h-3 rounded-full {true
                            ? 'bg-green-500'
                            : 'bg-red-500'}"
                    ></div>
                    <span class="text-sm"
                        >{true ? "Active" : "Inactive"}</span
                    >
                </div>
            </div>
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
                            <div class="flex items-center space-x-2">
                                <div
                                    class="w-3 h-3 rounded-full {getTemperatureStatusColor(cmu.temperature)}"
                                ></div>
                                <span class="text-sm text-gray-300">
                                    {formatValue(cmu.temperature, "°C", 1)}
                                </span>
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
                                                [2, 5]
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