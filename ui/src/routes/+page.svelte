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

    // TypeScript interfaces
    interface TelemetryData {
        overview?: {
            pack_voltage: number;
            battery_level: number;
            power_consumption: number;
            solar_input: number;
            distance_travelled: number;
            motor_temperature: number;
        };
    }

    interface SpeedStatus {
        speed: number;
        predicted: number;
        margin: number;
        status: "ok" | "error";
    }

    interface HistoricalData {
        timestamps: string[];
        speed: number[];
        battery: number[];
        power: number[];
        solar: number[];
    }

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

    // Dummy data state
    let data: TelemetryData = {
        overview: {
            pack_voltage: 48.2,
            battery_level: 87,
            power_consumption: 1250,
            solar_input: 450,
            distance_travelled: 142.8,
            motor_temperature: 68.5,
        },
    };

    let speed: SpeedStatus = {
        speed: 65.4,
        predicted: 67.2,
        margin: 1.8,
        status: "ok",
    };

    let history: HistoricalData = {
        timestamps: [],
        speed: [],
        battery: [],
        power: [],
        solar: [],
    };

    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)} ${unit}`;
    }

    function generateHistoricalData(): void {
        const now = new Date();
        const timestamps: string[] = [];
        const speedData: number[] = [];
        const batteryData: number[] = [];
        const powerData: number[] = [];
        const solarData: number[] = [];

        for (let i = 59; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60000);
            timestamps.push(time.toLocaleTimeString());

            speedData.push(60 + Math.sin(i / 10) * 15 + Math.random() * 5);
            batteryData.push(Math.max(20, 90 - i * 0.8 + Math.random() * 3));
            powerData.push(1000 + Math.sin(i / 8) * 400 + Math.random() * 100);
            solarData.push(
                Math.max(0, 400 + Math.sin(i / 12) * 200 + Math.random() * 50)
            );
        }

        history = {
            timestamps,
            speed: speedData,
            battery: batteryData,
            power: powerData,
            solar: solarData,
        };
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
                labels: history.timestamps,
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
        if (history.timestamps.length === 0) return;

        if (speedChart) {
            speedChart.data.labels = history.timestamps;
            speedChart.data.datasets[0].data = history.speed;
            speedChart.update("none");
        }

        if (batteryChart) {
            batteryChart.data.labels = history.timestamps;
            batteryChart.data.datasets[0].data = history.battery;
            batteryChart.update("none");
        }

        if (powerChart) {
            powerChart.data.labels = history.timestamps;
            powerChart.data.datasets[0].data = history.power;
            powerChart.update("none");
        }

        if (solarChart) {
            solarChart.data.labels = history.timestamps;
            solarChart.data.datasets[0].data = history.solar;
            solarChart.update("none");
        }
    }

    function updateLiveData(): void {
        // Update current metrics
        data = {
            overview: {
                ...data.overview!,
                battery_level: Math.max(0, data.overview!.battery_level - 0.1),
                power_consumption: 1250 + Math.random() * 200 - 100,
                solar_input: 450 + Math.random() * 100 - 50,
                distance_travelled: data.overview!.distance_travelled + 0.1,
                motor_temperature: 68.5 + Math.random() * 4 - 2,
            },
        };

        const newSpeed = 65 + Math.random() * 10 - 5;
        const newPredicted = newSpeed + Math.random() * 4 - 2;
        const newMargin = Math.abs(newSpeed - newPredicted);

        speed = {
            speed: newSpeed,
            predicted: newPredicted,
            margin: newMargin,
            status: newMargin < 3 ? "ok" : "error",
        };

        // Add new data point to history
        const newTimestamp = new Date().toLocaleTimeString();
        const newSpeedPoint =
            60 + Math.sin(Date.now() / 100000) * 15 + Math.random() * 5;
        const newBattery = Math.max(
            0,
            history.battery[history.battery.length - 1] -
                0.05 +
                Math.random() * 0.1
        );
        const newPower =
            1000 + Math.sin(Date.now() / 80000) * 400 + Math.random() * 100;
        const newSolar = Math.max(
            0,
            400 + Math.sin(Date.now() / 120000) * 200 + Math.random() * 50
        );

        history = {
            timestamps: [...history.timestamps.slice(-59), newTimestamp],
            speed: [...history.speed.slice(-59), newSpeedPoint],
            battery: [...history.battery.slice(-59), newBattery],
            power: [...history.power.slice(-59), newPower],
            solar: [...history.solar.slice(-59), newSolar],
        };
    }

    // Reactive statement to update charts when history changes
    $: if (history.timestamps.length > 0) {
        updateCharts();
    }

    onMount(() => {
        generateHistoricalData();

        // Create charts
        if (speedCanvas) {
            speedChart = new Chart(
                speedCanvas,
                createChartConfig(
                    "Speed",
                    history.speed,
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
                    history.battery,
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
                    history.power,
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
                    history.solar,
                    "#eab308",
                    "Solar Input (W)"
                )
            );
        }

        // Set up live data updates
        const interval = setInterval(updateLiveData, 5000);

        return () => {
            clearInterval(interval);
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
            class="metric-card col-span-1 md:col-span-2 {speed.status === 'ok'
                ? 'status-ok'
                : 'status-error'} border-2"
        >
            <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold">Speed Status</h3>
                <div
                    class="w-4 h-4 rounded-full {speed.status === 'ok'
                        ? 'bg-green-500'
                        : 'bg-red-500'}"
                ></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <div class="metric-value text-blue-400">
                        {formatValue(speed.speed, "km/h")}
                    </div>
                    <div class="metric-label">Current Speed</div>
                </div>
                <div>
                    <div class="metric-value text-gray-400">
                        {formatValue(speed.predicted, "km/h")}
                    </div>
                    <div class="metric-label">Predicted Speed</div>
                </div>
            </div>
            <div class="mt-2 text-sm">
                <span class="text-gray-400">Margin: </span>
                <span
                    class={speed.status === "ok"
                        ? "text-green-400"
                        : "text-red-400"}
                >
                    {formatValue(speed.margin, "km/h")}
                </span>
            </div>
        </div>

        <!-- Pack Voltage -->
        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue(data.overview?.pack_voltage, "V")}
            </div>
            <div class="metric-label">Pack Voltage</div>
        </div>

        <!-- Battery Level -->
        <div class="metric-card">
            <div class="metric-value text-green-400">
                {formatValue(data.overview?.battery_level, "%", 0)}
            </div>
            <div class="metric-label">Battery Level</div>
        </div>
    </div>

    <!-- Secondary Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue(data.overview?.power_consumption, "W", 0)}
            </div>
            <div class="metric-label">Power Consumption</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue(data.overview?.solar_input, "W", 0)}
            </div>
            <div class="metric-label">Solar Input</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue(data.overview?.distance_travelled, "km")}
            </div>
            <div class="metric-label">Distance Travelled</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400">
                {formatValue(data.overview?.motor_temperature, "°C")}
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
