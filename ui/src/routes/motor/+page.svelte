<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import * as Chart from "chart.js";
    import { globalStore } from "$lib/store";

    // Variables
    let busPowerCanvas: HTMLCanvasElement;
    let rpmCanvas: HTMLCanvasElement;
    let speedCanvas: HTMLCanvasElement;
    let busPowerChart: Chart.Chart;
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

    function updatePlots(): void {
        if ($globalStore.historic.Timestamps.length === 0) return;

        // Update Bus Power Chart
        if (busPowerChart) {
            busPowerChart.data.labels = $globalStore.historic.Timestamps;
            busPowerChart.data.datasets[0].data = $globalStore.historic.Bus_Power;
            busPowerChart.update("none");
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

        // Common chart options
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
            },
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: "#4B5563",
                    },
                    ticks: {
                        color: "#D1D5DB",
                        maxTicksLimit: 8,
                    },
                },
                y: {
                    display: true,
                    grid: {
                        color: "#4B5563",
                    },
                    ticks: {
                        color: "#D1D5DB",
                    },
                },
            },
            elements: {
                point: {
                    radius: 0,
                    hoverRadius: 4,
                },
            },
        };

        // Initialize Bus Power Chart
        if (busPowerCanvas) {
            busPowerChart = new Chart.Chart(busPowerCanvas, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Bus Power (W)",
                            data: [],
                            borderColor: "#f59e0b",
                            backgroundColor: "#f59e0b20",
                            tension: 0.4,
                            fill: true,
                        },
                    ],
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        title: {
                            display: true,
                            text: "Bus Power vs Time",
                            color: "#fff",
                            font: {
                                size: 16,
                            },
                        },
                    },
                },
            });
        }

        // Initialize RPM Chart
        if (rpmCanvas) {
            rpmChart = new Chart.Chart(rpmCanvas, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Motor RPM",
                            data: [],
                            borderColor: "#10b981",
                            backgroundColor: "#10b98120",
                            tension: 0.4,
                            fill: true,
                        },
                    ],
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        title: {
                            display: true,
                            text: "Motor RPM vs Time",
                            color: "#fff",
                            font: {
                                size: 16,
                            },
                        },
                    },
                },
            });
        }

        // Initialize Speed Chart
        if (speedCanvas) {
            speedChart = new Chart.Chart(speedCanvas, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Vehicle Speed (km/h)",
                            data: [],
                            borderColor: "#3b82f6",
                            backgroundColor: "#3b82f620",
                            tension: 0.4,
                            fill: true,
                        },
                    ],
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        title: {
                            display: true,
                            text: "Vehicle Speed vs Time",
                            color: "#fff",
                            font: {
                                size: 16,
                            },
                        },
                    },
                },
            });
        }
    });

    onDestroy(() => {
        // Clean up charts
        if (busPowerChart) busPowerChart.destroy();
        if (rpmChart) rpmChart.destroy();
        if (speedChart) speedChart.destroy();
    });

    // Status calculation functions
    function getMotorStatus(temperature: number): {
        color: string;
        text: string;
    } {
        if (temperature < 70) return { color: "bg-green-500", text: "Normal" };
        if (temperature < 85)
            return { color: "bg-yellow-500", text: "Warning" };
        return { color: "bg-red-500", text: "Critical" };
    }

    function getThermalStatus(heatsinkTemp: number): {
        color: string;
        text: string;
    } {
        if (heatsinkTemp < 60) return { color: "bg-green-500", text: "Cool" };
        if (heatsinkTemp < 75) return { color: "bg-yellow-500", text: "Warm" };
        return { color: "bg-red-500", text: "Hot" };
    }

    function getPowerStatus(busPower: number): { color: string; text: string } {
        if (busPower < 300) return { color: "bg-green-500", text: "Efficient" };
        if (busPower < 400) return { color: "bg-yellow-500", text: "High" };
        return { color: "bg-red-500", text: "Very High" };
    }

    // Reactive status calculations
    $: motorStatus = getMotorStatus($globalStore.metric.Motor_Temp || 0);
    $: thermalStatus = getThermalStatus($globalStore.metric.HeatSink_Temp || 0);
    $: powerStatus = getPowerStatus($globalStore.metric.Bus_Power || 0);
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
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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

    <!-- Motor Status Indicators -->
    <!-- <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Motor Status</span>
                <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full {motorStatus.color}"></div>
                    <span class="text-sm">{motorStatus.text}</span>
                </div>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Thermal Status</span>
                <div class="flex items-center space-x-2">
                    <div
                        class="w-3 h-3 rounded-full {thermalStatus.color}"
                    ></div>
                    <span class="text-sm">{thermalStatus.text}</span>
                </div>
            </div>
        </div>

        <div class="metric-card">
            <div class="flex items-center justify-between">
                <span class="metric-label">Power Status</span>
                <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full {powerStatus.color}"></div>
                    <span class="text-sm">{powerStatus.text}</span>
                </div>
            </div>
        </div>
    </div> -->

    <!-- Performance Charts -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div class="plot-container">
            <canvas bind:this={busPowerCanvas} class="w-full h-80"></canvas>
        </div>

        <div class="plot-container">
            <canvas bind:this={rpmCanvas} class="w-full h-80"></canvas>
        </div>
    </div>

    <div class="plot-container">
        <canvas bind:this={speedCanvas} class="w-full h-80"></canvas>
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
