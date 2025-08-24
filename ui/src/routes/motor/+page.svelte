<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import * as Chart from "chart.js";
    import { globalStore } from "$lib/store";
    import type { TelemetryData } from '$lib/store_types';

    // Variables
    let busPowerCanvas: HTMLCanvasElement;
    let phaseACanvas: HTMLCanvasElement;
    let rpmCanvas: HTMLCanvasElement;
    let speedCanvas: HTMLCanvasElement;
    let busPowerChart: Chart.Chart;
    let phaseAChart: Chart.Chart;
    let rpmChart: Chart.Chart;
    let speedChart: Chart.Chart;

    // Utility functions
    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function createChartConfig(
        label: string,
        data: number[],
        color: string,
        yAxisLabel: string
    ): Chart.ChartConfiguration {
        return {
            type: "line",
            data: {
                labels: $globalStore.historic.Timestamps,
                datasets: [
                    {
                        label: label,
                        data: data,
                        borderColor: color,
                        backgroundColor: color + "20",
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: label === "Battery Level",
                        max: label === "Battery Level" ? 100 : undefined,
                        title: {
                            display: true,
                            text: yAxisLabel,
                            color: "#fff",
                        },
                        ticks: {
                            color: "#fff",
                        },
                        grid: {
                            color: "#374151",
                        },
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Time",
                            color: "#fff",
                        },
                        ticks: {
                            color: "#fff",
                        },
                        grid: {
                            color: "#374151",
                        },
                    },
                },
                plugins: {
                    legend: {
                        labels: {
                            color: "#fff",
                        },
                    },
                    title: {
                        display: true,
                        text: `${label} vs Time`,
                        color: "#fff",
                    },
                },
            },
        };
    }

    function updatePlots(): void {
        if ($globalStore.historic.Timestamps.length === 0) return;

        // Update Bus Power Chart
        if (busPowerChart) {
            busPowerChart.data.labels = $globalStore.historic.Timestamps;
            busPowerChart.data.datasets[0].data = $globalStore.historic.Bus_Power;
            busPowerChart.update("none");
        }
        
        // Update Phase A Current Chart
        if (phaseAChart) {
            phaseAChart.data.labels = $globalStore.historic.Timestamps;
            phaseAChart.data.datasets[0].data = $globalStore.historic.PhaseA_Current;
            phaseAChart.update("none");
        }

        // Update RPM Chart
        if (rpmChart) {
            rpmChart.data.labels = $globalStore.historic.Timestamps;
            rpmChart.data.datasets[0].data = $globalStore.historic.Motor_Velocity;
            rpmChart.update("none");
        }

        // Update Speed Chart
        if (speedChart) {
            speedChart.data.labels = $globalStore.historic.Timestamps;
            speedChart.data.datasets[0].data = $globalStore.historic.Speed2;
            speedChart.update("none");
        }
    }

    $: if ($globalStore.historic.Timestamps.length > 0) {
        updatePlots();
    }

    onMount(() => {
        // Register Chart.js components
        Chart.Chart.register(
            Chart.CategoryScale,
            Chart.LinearScale,
            Chart.PointElement,
            Chart.LineElement,
            Chart.LineController,
            Chart.Title,
            Chart.Tooltip,
            Chart.Legend
        );

        // Initialize Bus Power Chart
        if (busPowerCanvas) {
            busPowerChart = new Chart.Chart(
                busPowerCanvas,
                createChartConfig(
                    "Bus Power",
                    $globalStore.historic.Bus_Power,
                    "#f59e0b",
                    "Bus Power (W)"
                )
            );
        }

        // Initialise Phase A Current Canvas
        if (phaseACanvas) {
            phaseAChart = new Chart.Chart(
                phaseACanvas,
                createChartConfig(
                    "Phase A Current",
                    $globalStore.historic.PhaseA_Current,
                    "#ab47bc",
                    "Bus Power (W)"
                )
            );
        }

        // Initialize RPM Chart
        if (rpmCanvas) {
            rpmChart = new Chart.Chart(
                rpmCanvas,
                createChartConfig(
                    "Motor RPM",
                    $globalStore.historic.Motor_Velocity,
                    "#10b981",
                    "Motor RPM vs Time"
                )
            );
        }

        // Initialize Speed Chart
        if (speedCanvas) {
            speedChart = new Chart.Chart(
                speedCanvas,
                createChartConfig(
                    "Vehicle Speed (km/h)",
                    $globalStore.historic.Speed2,
                    "#3b82f6",
                    "Vehicle Speed vs Time"
                )
            );
        }
    });

    onDestroy(() => {
        // Clean up charts
        if (busPowerChart) busPowerChart.destroy();
        if (rpmChart) rpmChart.destroy();
        if (speedChart) speedChart.destroy();
    });

    interface limitItem{
        key: keyof TelemetryData['metric']['MotorLimits'];
        label: string;
    }

    interface errorItem{
        key: keyof TelemetryData['metric']['MotorErrors'];
        label: string;
    }

    // Limit flags configuration
    const limitLabels:  limitItem[] = [
        { key: 'ipm_temp_limit', label: 'IPM Temp' },
        { key: 'bus_voltage_lower_limit', label: 'Bus V Low' },
        { key: 'bus_voltage_upper_limit', label: 'Bus V High' },
        { key: 'bus_current_limit', label: 'Bus Current' },
        { key: 'velocity_limit', label: 'Velocity' },
        { key: 'motor_current_limit', label: 'Motor Current' },
        { key: 'output_voltage_pwm_limit', label: 'Output PWM' }
    ];

    // Error flags configuration
    const errorLabels: errorItem[] = [
        { key: 'motor_over_speed', label: 'Over Speed' },
        { key: 'desaturation_fault', label: 'Desaturation' },
        { key: 'rail_15v_uvlo', label: '15V UVLO' },
        { key: 'config_read_error', label: 'Config Error' },
        { key: 'watchdog_reset', label: 'Watchdog' },
        { key: 'bad_motor_position', label: 'Hall Sequence' },
        { key: 'dc_bus_over_voltage', label: 'DC Bus OV' },
        { key: 'software_over_current', label: 'SW OC' },
        { key: 'hardware_over_current', label: 'HW OC' }
    ];

    // Reactive statements to extract flags from your global store
    // Adjust these based on your actual data structure
    $: limitFlags = {
        ipm_temp_limit: $globalStore.metric.MotorLimits.ipm_temp_limit,
        bus_voltage_lower_limit: $globalStore.metric.MotorLimits.bus_voltage_lower_limit,
        bus_voltage_upper_limit: $globalStore.metric.MotorLimits.bus_voltage_upper_limit,
        bus_current_limit: $globalStore.metric.MotorLimits.bus_current_limit,
        velocity_limit: $globalStore.metric.MotorLimits.velocity_limit,
        motor_current_limit: $globalStore.metric.MotorLimits.motor_current_limit,
        output_voltage_pwm_limit: $globalStore.metric.MotorLimits.output_voltage_pwm_limit
    };

    $: errorFlags = {
        motor_over_speed: $globalStore.metric.MotorErrors.motor_over_speed,
        desaturation_fault: $globalStore.metric.MotorErrors.desaturation_fault,
        rail_15v_uvlo: $globalStore.metric.MotorErrors.rail_15v_uvlo,
        config_read_error: $globalStore.metric.MotorErrors.config_read_error,
        watchdog_reset: $globalStore.metric.MotorErrors.watchdog_reset,
        bad_motor_position: $globalStore.metric.MotorErrors.bad_motor_position,
        dc_bus_over_voltage: $globalStore.metric.MotorErrors.dc_bus_over_voltage,
        software_over_current: $globalStore.metric.MotorErrors.software_over_current,
        hardware_over_current: $globalStore.metric.MotorErrors.hardware_over_current
    };
</script>

<div class="space-y-6 p-6">
    <!-- Primary Motor Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="metric-card">
            <div class="metric-value text-green-400 text-2xl">
                {formatValue($globalStore.metric.Motor_Velocity, "RPM", 0)}
            </div>
            <div class="metric-label">Motor RPM</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-blue-400 text-2xl">
                {formatValue($globalStore.metric.Speed2, "km/h")}
            </div>
            <div class="metric-label">Velocity</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400 text-2xl">
                {formatValue($globalStore.metric.Motor_Temp, "°C")}
            </div>
            <div class="metric-label">Motor Temperature</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-cyan-400 text-2xl">
                {formatValue($globalStore.metric.HeatSink_Temp, "°C")}
            </div>
            <div class="metric-label">Heatsink Temperature</div>
        </div>
    </div>

    <!-- Phase Current and Bus Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue($globalStore.metric.PhaseA_Current, "A")}
            </div>
            <div class="metric-label">Phase Current A</div>
        </div>
    
        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue($globalStore.metric.PhaseB_Current, "A")}
            </div>
            <div class="metric-label">Phase Current B</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue($globalStore.metric.PhaseC_Current, "A")}
            </div>
            <div class="metric-label">Phase Current C</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue($globalStore.metric.Bus_Voltage, "V")}
            </div>
            <div class="metric-label">Bus Voltage</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue($globalStore.metric.Bus_Current, "A")}
            </div>
            <div class="metric-label">Bus Current</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400">
                {formatValue($globalStore.metric.Bus_Power, "W", 0)}
            </div>
            <div class="metric-label">Bus Power</div>
        </div>
    </div>

    <!-- Motor Limit Flags -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-gray-400">Motor Limit Status:</span>
        </div>
        <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {#each limitLabels as flag}
                {@const isActive = limitFlags[flag.key as keyof typeof limitFlags]}
                <div class="flex items-center justify-center space-x-1">
                    <div class="w-3 h-3 rounded-full {isActive ? 'bg-yellow-500' : 'bg-gray-500'} flex-shrink-0"></div>
                    <span class="text-xs text-gray-300">{flag.label}</span>
                </div>
            {/each}
        </div>
    </div>

    <!-- Motor Error Flags -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-gray-400">Motor Error Status:</span>
        </div>
        <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {#each errorLabels as flag}
                {@const isActive = errorFlags[flag.key as keyof typeof errorFlags]}
                <div class="flex items-center justify-center space-x-1">
                    <div class="w-3 h-3 rounded-full {isActive ? 'bg-red-500' : 'bg-gray-500'} flex-shrink-0"></div>
                    <span class="text-xs text-gray-300">{flag.label}</span>
                </div>
            {/each}
        </div>
    </div>


    <!-- Performance Charts -->
    <div class="plot-container">
        <canvas bind:this={busPowerCanvas} class="w-full h-80"></canvas>
    </div>

    <div class="plot-container">
        <canvas bind:this={speedCanvas} class="w-full h-80"></canvas>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div class="plot-container">
            <canvas bind:this={phaseACanvas} class="w-full h-80"></canvas>
        </div>
        
        <div class="plot-container">
            <canvas bind:this={rpmCanvas} class="w-full h-80"></canvas>
        </div>
    </div>

    <!-- Motor Efficiency Calculation -->
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 class="text-lg font-semibold mb-4">Motor Efficiency Analysis</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-400">
                    {formatValue(
                        (($globalStore.metric.Speed2 || 0) / ($globalStore.metric.Motor_Velocity || 1)) * 60,
                        "m/rev",
                        3
                    )}
                </div>
                <div class="text-sm text-gray-400">Distance per Revolution</div>
            </div>

            <div class="text-center">
                <div class="text-2xl font-bold text-green-400">
                    {formatValue(
                        ($globalStore.metric.Bus_Power || 0) / ($globalStore.metric.Speed2 || 1),
                        "W⋅h/km",
                        1
                    )}
                </div>
                <div class="text-sm text-gray-400">Power per Speed</div>
            </div>

            <div class="text-center">
                <div class="text-2xl font-bold text-purple-400">
                    {formatValue(
                        (($globalStore.metric.PhaseB_Current || 0) +
                            ($globalStore.metric.PhaseC_Current || 0)) /
                            2,
                        "A",
                        2
                    )}
                </div>
                <div class="text-sm text-gray-400">Average Phase Current</div>
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

    .plot-container {
        @apply bg-gray-800 rounded-lg p-4 border border-gray-700;
    }
</style>
