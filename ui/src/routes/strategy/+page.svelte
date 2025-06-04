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
    import { globalStore } from "$lib/store";

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

    // Canvas element references
    let speedCombinedCanvas: HTMLCanvasElement;
    let accelerationCanvas: HTMLCanvasElement;
    let altitudeCanvas: HTMLCanvasElement;
    let powerCanvas: HTMLCanvasElement;
    let solarCanvas: HTMLCanvasElement;
    let batteryCanvas: HTMLCanvasElement;

    // Chart instances
    let speedCombinedChart: Chart;
    let accelerationChart: Chart;
    let altitudeChart: Chart;
    let powerChart: Chart;
    let solarChart: Chart;
    let batteryChart: Chart;

    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function createSingleChartConfig(
        label: string,
        data: number[],
        color: string,
        yAxisLabel: string,
        beginAtZero: boolean = false,
        maxValue?: number
    ): ChartConfiguration {
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
                        beginAtZero: beginAtZero,
                        max: maxValue,
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

    function createCombinedSpeedChartConfig(): ChartConfiguration {
        return {
            type: "line",
            data: {
                labels: $globalStore.historic.Timestamps,
                datasets: [
                    {
                        label: "Speed",
                        data: $globalStore.historic.Speed,
                        borderColor: "#3b82f6",
                        backgroundColor: "#3b82f620",
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                    },
                    {
                        label: "Speed 2",
                        data: $globalStore.historic.Speed2 || [],
                        borderColor: "#ef4444",
                        backgroundColor: "#ef444420",
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
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Speed (km/h)",
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
                        text: "Speed & Speed 2 vs Time",
                        color: "#fff",
                    },
                },
            },
        };
    }

    function updateCharts(): void {
        if ($globalStore.historic.Timestamps.length === 0) return;

        if (speedCombinedChart) {
            speedCombinedChart.data.labels = $globalStore.historic.Timestamps;
            speedCombinedChart.data.datasets[0].data = $globalStore.historic.Speed;
            speedCombinedChart.data.datasets[1].data = $globalStore.historic.Speed2 || [];
            speedCombinedChart.update("none");
        }

        if (accelerationChart) {
            accelerationChart.data.labels = $globalStore.historic.Timestamps;
            accelerationChart.data.datasets[0].data = $globalStore.historic.Acceleration || [];
            accelerationChart.update("none");
        }

        if (altitudeChart) {
            altitudeChart.data.labels = $globalStore.historic.Timestamps;
            altitudeChart.data.datasets[0].data = $globalStore.historic.Altitude || [];
            altitudeChart.update("none");
        }

        if (powerChart) {
            powerChart.data.labels = $globalStore.historic.Timestamps;
            powerChart.data.datasets[0].data = $globalStore.historic.Power;
            powerChart.update("none");
        }

        if (solarChart) {
            solarChart.data.labels = $globalStore.historic.Timestamps;
            solarChart.data.datasets[0].data = $globalStore.historic.Solar;
            solarChart.update("none");
        }

        if (batteryChart) {
            batteryChart.data.labels = $globalStore.historic.Timestamps;
            batteryChart.data.datasets[0].data = $globalStore.historic.Battery;
            batteryChart.update("none");
        }
    }

    // Reactive statement to update charts when history changes
    $effect(() => {
        if ($globalStore.historic.Timestamps.length > 0) {
            updateCharts();
        }
    });

    onMount(() => {
        // Create combined speed chart
        if (speedCombinedCanvas) {
            speedCombinedChart = new Chart(
                speedCombinedCanvas,
                createCombinedSpeedChartConfig()
            );
        }

        // Create acceleration chart
        if (accelerationCanvas) {
            accelerationChart = new Chart(
                accelerationCanvas,
                createSingleChartConfig(
                    "Acceleration",
                    $globalStore.historic.Acceleration || [],
                    "#8b5cf6",
                    "Acceleration (m/s²)"
                )
            );
        }

        // Create altitude chart
        if (altitudeCanvas) {
            altitudeChart = new Chart(
                altitudeCanvas,
                createSingleChartConfig(
                    "Altitude",
                    $globalStore.historic.Altitude || [],
                    "#06b6d4",
                    "Altitude (m)"
                )
            );
        }

        // Create power chart
        if (powerCanvas) {
            powerChart = new Chart(
                powerCanvas,
                createSingleChartConfig(
                    "Power Consumption",
                    $globalStore.historic.Power,
                    "#f59e0b",
                    "Power (W)",
                    true
                )
            );
        }

        // Create solar chart
        if (solarCanvas) {
            solarChart = new Chart(
                solarCanvas,
                createSingleChartConfig(
                    "Solar Input",
                    $globalStore.historic.Solar,
                    "#eab308",
                    "Solar Input (W)",
                    true
                )
            );
        }

        // Create battery chart
        if (batteryCanvas) {
            batteryChart = new Chart(
                batteryCanvas,
                createSingleChartConfig(
                    "Battery Level",
                    $globalStore.historic.Battery,
                    "#10b981",
                    "Battery Level (%)",
                    true,
                    100
                )
            );
        }

        return () => {
            // Cleanup charts
            speedCombinedChart?.destroy();
            accelerationChart?.destroy();
            altitudeChart?.destroy();
            powerChart?.destroy();
            solarChart?.destroy();
            batteryChart?.destroy();
        };
    });

    const speed_margin = $derived(Math.abs($globalStore.metric.Speed - $globalStore.metric.predicted));
    const speed_status = $derived(speed_margin > 3 ? 'error' : 'ok');

</script>

<div class="space-y-6 p-6">
    <!-- Key Current Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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
                        {formatValue($globalStore.metric.Speed, "km/h")}
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

        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue($globalStore.historic.Acceleration[-1], "m/s²")}
            </div>
            <div class="metric-label">Current Acceleration</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-green-400">
                {formatValue($globalStore.metric.SOC_Ah, "%", 0)}
            </div>
            <div class="metric-label">Battery Level</div>
        </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <!-- Combined Speed Chart -->
        <div class="plot-container xl:col-span-2">
            <canvas bind:this={speedCombinedCanvas} class="w-full h-80"></canvas>
        </div>

        <!-- Acceleration Chart -->
        <div class="plot-container">
            <canvas bind:this={accelerationCanvas} class="w-full h-80"></canvas>
        </div>

        <!-- Altitude Chart -->
        <div class="plot-container">
            <canvas bind:this={altitudeCanvas} class="w-full h-80"></canvas>
        </div>

        <!-- Power Consumption Chart -->
        <div class="plot-container">
            <canvas bind:this={powerCanvas} class="w-full h-80"></canvas>
        </div>

        <!-- Solar Input Chart -->
        <div class="plot-container">
            <canvas bind:this={solarCanvas} class="w-full h-80"></canvas>
        </div>

        <!-- Battery Level Chart -->
        <div class="plot-container xl:col-span-2">
            <canvas bind:this={batteryCanvas} class="w-full h-80"></canvas>
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

    .status-ok {
        @apply border-green-500;
    }

    .status-error {
        @apply border-red-500;
    }

    .plot-container {
        @apply bg-gray-800 rounded-lg p-4 border border-gray-700;
    }
</style>