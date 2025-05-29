<script lang="ts">
    import { onMount } from "svelte";
    import {
        Chart,
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        LineController,
        Title,
        Tooltip,
        Legend,
        type ChartConfiguration,
    } from "chart.js";
    import {globalStore} from "$lib/store";

    // Register Chart.js components
    Chart.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        LineController,
        Title,
        Tooltip,
        Legend
    );

    const speed_margin = $derived(Math.abs($globalStore.metric.speed - $globalStore.metric.predicted));
    const speed_status = $derived(speed_margin > 3 ? 'error' : 'ok');

    // Canvas element references
    let speedCanvas: HTMLCanvasElement;
    let batteryCanvas: HTMLCanvasElement;
    let powerCanvas: HTMLCanvasElement;
    let solarCanvas: HTMLCanvasElement;

    // Chart instances
    let speedChart: Chart;
    let batteryChart: Chart;
    let powerChart: Chart;
    let solarChart: Chart;

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
    ): ChartConfiguration {
        return {
            type: "line",
            data: {
                labels: $globalStore.historic.timestamps,
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

    function updateCharts(): void {
        if ($globalStore.historic.timestamps.length === 0) return;

        if (speedChart) {
            speedChart.data.labels = $globalStore.historic.timestamps;
            speedChart.data.datasets[0].data = $globalStore.historic.speed;
            speedChart.update("none");
        }

        if (batteryChart) {
            batteryChart.data.labels = $globalStore.historic.timestamps;
            batteryChart.data.datasets[0].data = $globalStore.historic.battery;
            batteryChart.update("none");
        }

        if (powerChart) {
            powerChart.data.labels = $globalStore.historic.timestamps;
            powerChart.data.datasets[0].data = $globalStore.historic.power;
            powerChart.update("none");
        }

        if (solarChart) {
            solarChart.data.labels = $globalStore.historic.timestamps;
            solarChart.data.datasets[0].data = $globalStore.historic.solar;
            solarChart.update("none");
        }
    }

    // Reactive statement to update charts when history changes
    $effect(() => {
        if ($globalStore.historic.timestamps.length > 0) {
            updateCharts();
        }
    });

    onMount(() => {
        // Create charts
        if (speedCanvas) {
            speedChart = new Chart(
                speedCanvas,
                createChartConfig(
                    "Speed",
                    $globalStore.historic.speed,
                    "#3b82f6",
                    "Speed (km/h)"
                )
            );
        }
        if (batteryCanvas) {
            batteryChart = new Chart(
                batteryCanvas,
                createChartConfig(
                    "Battery Level",
                    $globalStore.historic.battery,
                    "#10b981",
                    "Battery Level (%)"
                )
            );
        }
        if (powerCanvas) {
            powerChart = new Chart(
                powerCanvas,
                createChartConfig(
                    "Power Consumption",
                    $globalStore.historic.power,
                    "#f59e0b",
                    "Power (W)"
                )
            );
        }
        if (solarCanvas) {
            solarChart = new Chart(
                solarCanvas,
                createChartConfig(
                    "Solar Input",
                    $globalStore.historic.solar,
                    "#eab308",
                    "Solar Input (W)"
                )
            );
        }

        return () => {
            // Cleanup charts
            speedChart?.destroy();
            batteryChart?.destroy();
            powerChart?.destroy();
            solarChart?.destroy();
        };
    });
</script>

<div class="space-y-6 p-6">
    <!-- Key Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Speed Status Card -->
        <div
            class="metric-card col-span-1 md:col-span-2 {speed_status === 'ok'
                ? 'status-ok'
                : 'status-error'} border-2"
        >
            <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold">Speed Status</h3>
                <div
                    class="w-4 h-4 rounded-full {speed_status === 'ok'
                        ? 'bg-green-500'
                        : 'bg-red-500'}"
                ></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <div class="metric-value text-blue-400">
                        {formatValue($globalStore.metric.speed, "km/h")}
                    </div>
                    <div class="metric-label">Current Speed</div>
                </div>
                <div>
                    <div class="metric-value text-gray-400">
                        {formatValue($globalStore.metric.predicted, "km/h")}
                    </div>
                    <div class="metric-label">Predicted Speed</div>
                </div>
            </div>
            <div class="mt-2 text-sm">
                <span class="text-gray-400">Margin: </span>
                <span
                    class={speed_status === "ok"
                        ? "text-green-400"
                        : "text-red-400"}
                >
                    {formatValue(speed_margin, "km/h")}
                </span>
            </div>
        </div>

        <!-- Pack Voltage -->
        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue($globalStore.metric.pack_voltage, "V")}
            </div>
            <div class="metric-label">Pack Voltage</div>
        </div>

        <!-- Battery Level -->
        <div class="metric-card">
            <div class="metric-value text-green-400">
                {formatValue($globalStore.metric.battery_level, "%", 0)}
            </div>
            <div class="metric-label">Battery Level</div>
        </div>
    </div>

    <!-- Secondary Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue($globalStore.metric.power_consumption, "W", 0)}
            </div>
            <div class="metric-label">Power Consumption</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue($globalStore.metric.solar_input, "W", 0)}
            </div>
            <div class="metric-label">Solar Input</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue($globalStore.metric.distance_travelled, "km")}
            </div>
            <div class="metric-label">Distance Travelled</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400">
                {formatValue($globalStore.metric.motor_temperature, "°C")}
            </div>
            <div class="metric-label">Motor Temperature</div>
        </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div class="plot-container">
            <canvas bind:this={speedCanvas} class="w-full h-80"></canvas>
        </div>

        <div class="plot-container">
            <canvas bind:this={batteryCanvas} class="w-full h-80"></canvas>
        </div>

        <div class="plot-container">
            <canvas bind:this={powerCanvas} class="w-full h-80"></canvas>
        </div>

        <div class="plot-container">
            <canvas bind:this={solarCanvas} class="w-full h-80"></canvas>
        </div>
    </div>
</div>

<style lang='postcss'>
    @reference "tailwindcss";

    .metric-card {
        @apply bg-gray-800 rounded-lg p-4;
    }

    .metric-value {
        @apply text-2xl font-bold;
    }

    .metric-label {
        @apply text-sm text-gray-400;
    }

    .status-ok {
        @apply border-green-500;
    }

    .status-error {
        @apply border-red-500;
    }

    .plot-container {
        @apply bg-gray-800 rounded-lg p-4;
    }
</style>
