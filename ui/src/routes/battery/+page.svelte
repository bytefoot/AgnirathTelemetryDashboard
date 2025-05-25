<script lang="ts">
    // import { telemetryData } from "$lib/stores/telemetry.js";

    // Type definitions
    interface Cell {
        voltage: number;
        temperature: number;
    }

    interface Pack {
        cells: Cell[];
    }

    interface Battery {
        state_of_charge: number;
        pack_voltage: number;
        pack_current: number;
        max_temperature: number;
        min_temperature: number;
        voltage_range: [number, number];
        temperature_range: [number, number];
        precharge_state: boolean;
        packs: Pack[];
    }

    interface TelemetryData {
        battery: Battery;
    }

    // Dummy data generator - comment/uncomment as needed
    function generateDummyData(): TelemetryData {
        const generateCells = (): Cell[] => {
            return Array.from({ length: 14 }, () => ({
                voltage: 3.2 + Math.random() * 0.6, // Random voltage between 3.2V and 3.8V
                temperature: 25 + Math.random() * 15 // Random temp between 25°C and 40°C
            }));
        };

        return {
            battery: {
                state_of_charge: 75 + Math.random() * 20, // 75-95%
                pack_voltage: 45.6 + Math.random() * 5, // Around 48V nominal
                pack_current: -10 + Math.random() * 20, // -10A to +10A
                max_temperature: 35 + Math.random() * 10,
                min_temperature: 25 + Math.random() * 5,
                voltage_range: [3.0, 4.0],
                temperature_range: [20, 60],
                precharge_state: Math.random() > 0.3, // 70% chance active
                packs: Array.from({ length: 5 }, () => ({
                    cells: generateCells()
                }))
            }
        };
    }

    // State variables
    let data: TelemetryData = generateDummyData(); // Using dummy data
    let selectedPack: number = 0;
    let selectedView: 'voltage' | 'temperature' = "voltage";

    // Reactive statements
    $: battery = data.battery || {} as Battery;
    $: packs = battery.packs || [];

    // Utility functions
    function formatValue(value: number | undefined, unit: string = "", decimals: number = 2): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function getStatusColor(value: number | undefined, range?: [number, number], isTemperature: boolean = false): string {
        if (typeof value !== "number") return "bg-gray-600";

        if (isTemperature) {
            if (value > 45) return "bg-red-500";
            if (value > 35) return "bg-yellow-500";
            return "bg-green-500";
        } else {
            // Voltage
            const [min, max] = range || [3.0, 4.0];
            const ratio = (value - min) / (max - min);
            if (ratio < 0.2 || ratio > 0.9) return "bg-red-500";
            if (ratio < 0.3 || ratio > 0.8) return "bg-yellow-500";
            return "bg-green-500";
        }
    }

    function getProgressWidth(value: number | undefined, isTemperature: boolean = false): number {
        if (typeof value !== "number") return 0;
        
        if (isTemperature) {
            return Math.min(100, Math.max(0, ((value - 20) / (60 - 20)) * 100));
        } else {
            return Math.min(100, Math.max(0, ((value - 3.0) / (4.0 - 3.0)) * 100));
        }
    }

    // Uncomment to use real telemetry data instead of dummy data
    // $: data = $telemetryData;
</script>

<div class="space-y-6 p-6">
    <!-- Main Battery Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="metric-card col-span-1 md:col-span-2">
            <div class="metric-value text-green-400 text-3xl">
                {formatValue(battery.state_of_charge, "%", 0)}
            </div>
            <div class="metric-label">State of Charge</div>
            <div class="mt-2 bg-gray-700 rounded-full h-2">
                <div
                    class="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style="width: {battery.state_of_charge || 0}%"
                ></div>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue(battery.pack_voltage, "V")}
            </div>
            <div class="metric-label">Pack Voltage</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-blue-400">
                {formatValue(battery.pack_current, "A")}
            </div>
            <div class="metric-label">Pack Current</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue(battery.max_temperature, "°C")}
            </div>
            <div class="metric-label">Max Temperature</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-cyan-400">
                {formatValue(battery.min_temperature, "°C")}
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
                    {formatValue(battery.voltage_range?.[0], "V")} - {formatValue(
                        battery.voltage_range?.[1],
                        "V"
                    )}
                </span>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Temperature Range</span>
                <span class="text-sm text-gray-300">
                    {formatValue(battery.temperature_range?.[0], "°C")} - {formatValue(
                        battery.temperature_range?.[1],
                        "°C"
                    )}
                </span>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Pre-charge State</span>
                <div class="flex items-center space-x-2">
                    <div
                        class="w-3 h-3 rounded-full {battery.precharge_state
                            ? 'bg-green-500'
                            : 'bg-red-500'}"
                    ></div>
                    <span class="text-sm"
                        >{battery.precharge_state ? "Active" : "Inactive"}</span
                    >
                </div>
            </div>
        </div>
    </div>

    <!-- Pack Selection and View Toggle -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div
            class="flex flex-col md:flex-row md:items-center md:justify-between mb-4"
        >
            <h3 class="text-lg font-semibold mb-2 md:mb-0">
                Battery Pack Details
            </h3>

            <div class="flex flex-col sm:flex-row gap-2">
                <!-- Pack Selection -->
                <div class="flex space-x-1">
                    {#each Array(5) as _, i}
                        <button
                            class="px-3 py-1 rounded {selectedPack === i
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
                            on:click={() => (selectedPack = i)}
                        >
                            Pack {i + 1}
                        </button>
                    {/each}
                </div>

                <!-- View Toggle -->
                <div class="flex space-x-1">
                    <button
                        class="px-3 py-1 rounded {selectedView === 'voltage'
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
                        on:click={() => (selectedView = "voltage")}
                    >
                        Voltage
                    </button>
                    <button
                        class="px-3 py-1 rounded {selectedView === 'temperature'
                            ? 'bg-orange-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
                        on:click={() => (selectedView = "temperature")}
                    >
                        Temperature
                    </button>
                </div>
            </div>
        </div>

        <!-- Cell Grid -->
        {#if packs[selectedPack]?.cells}
            <div class="grid grid-cols-7 gap-3">
                {#each packs[selectedPack].cells as cell, i}
                    <div class="bg-gray-700 rounded p-3 text-center">
                        <div class="text-xs text-gray-400 mb-1">
                            Cell {i + 1}
                        </div>
                        <div class="text-sm font-medium mb-2">
                            {#if selectedView === "voltage"}
                                {formatValue(cell.voltage, "V", 3)}
                            {:else}
                                {formatValue(cell.temperature, "°C", 1)}
                            {/if}
                        </div>
                        <div class="w-full h-2 rounded-full bg-gray-600">
                            <div
                                class="h-2 rounded-full {getStatusColor(
                                    selectedView === 'voltage'
                                        ? cell.voltage
                                        : cell.temperature,
                                    battery.voltage_range,
                                    selectedView === 'temperature'
                                )}"
                                style="width: {getProgressWidth(
                                    selectedView === 'voltage'
                                        ? cell.voltage
                                        : cell.temperature,
                                    selectedView === 'temperature'
                                )}%"
                            ></div>
                        </div>
                    </div>
                {/each}
            </div>
        {:else}
            <div class="text-center text-gray-400 py-8">
                No cell data available for Pack {selectedPack + 1}
            </div>
        {/if}

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