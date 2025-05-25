<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import * as Chart from "chart.js";
    // import { telemetryData, historicalData } from '$lib/stores/telemetry.js';

    // Type definitions
    interface Motor {
        rpm: number;
        velocity: number;
        temperature: number;
        heatsink_temp: number;
        phase_current_b: number;
        phase_current_c: number;
        bus_voltage: number;
        bus_current: number;
        bus_power: number;
    }

    interface TelemetryData {
        motor: Motor;
    }

    interface HistoricalData {
        timestamps: string[];
        buspower: number[];
        rpm: number[];
        speed: number[];
    }

    // Variables
    let busPowerCanvas: HTMLCanvasElement;
    let rpmCanvas: HTMLCanvasElement;
    let speedCanvas: HTMLCanvasElement;
    let busPowerChart: Chart.Chart;
    let rpmChart: Chart.Chart;
    let speedChart: Chart.Chart;

    // Dummy data generators - comment/uncomment as needed
    function generateDummyTelemetryData(): TelemetryData {
        return {
            motor: {
                rpm: 1200 + Math.random() * 800, // 1200-2000 RPM
                velocity: 25 + Math.random() * 15, // 25-40 km/h
                temperature: 45 + Math.random() * 25, // 45-70°C
                heatsink_temp: 35 + Math.random() * 20, // 35-55°C
                phase_current_b: 15 + Math.random() * 10, // 15-25 A
                phase_current_c: 15 + Math.random() * 10, // 15-25 A
                bus_voltage: 46 + Math.random() * 6, // 46-52 V
                bus_current: 8 + Math.random() * 6, // 8-14 A
                bus_power: 300 + Math.random() * 200, // 300-500 W
            },
        };
    }

    function generateDummyHistoricalData(): HistoricalData {
        const now = new Date();
        const timestamps: string[] = [];
        const buspower: number[] = [];
        const rpm: number[] = [];
        const speed: number[] = [];

        // Generate 50 data points over the last 5 minutes
        for (let i = 49; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 6000); // 6 seconds apart
            timestamps.push(time.toISOString());

            // Generate realistic trends
            const baseRpm = 1500 + Math.sin(i * 0.1) * 300;
            const baseSpeed = 30 + Math.sin(i * 0.1) * 8;
            const basePower = 350 + Math.sin(i * 0.15) * 100;

            rpm.push(baseRpm + (Math.random() - 0.5) * 100);
            speed.push(baseSpeed + (Math.random() - 0.5) * 5);
            buspower.push(basePower + (Math.random() - 0.5) * 50);
        }

        return { timestamps, buspower, rpm, speed };
    }

    // State variables with dummy data
    let data: TelemetryData = generateDummyTelemetryData();
    let history: HistoricalData = generateDummyHistoricalData();

    // Reactive statements
    $: motor = data.motor || ({} as Motor);

    // Uncomment to use real telemetry data instead of dummy data
    // $: data = $telemetryData;
    // $: history = $historicalData;

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
        if (history.timestamps.length === 0) return;

        // Format timestamps for display
        const formattedTimestamps = history.timestamps.map((ts) => {
            const date = new Date(ts);
            return date.toLocaleTimeString("en-US", {
                hour12: false,
                minute: "2-digit",
                second: "2-digit",
            });
        });

        // Update Bus Power Chart
        if (busPowerChart) {
            busPowerChart.data.labels = formattedTimestamps;
            busPowerChart.data.datasets[0].data = history.buspower;
            busPowerChart.update("none");
        }

        // Update RPM Chart
        if (rpmChart) {
            rpmChart.data.labels = formattedTimestamps;
            rpmChart.data.datasets[0].data = history.rpm;
            rpmChart.update("none");
        }

        // Update Speed Chart
        if (speedChart) {
            speedChart.data.labels = formattedTimestamps;
            speedChart.data.datasets[0].data = history.speed;
            speedChart.update("none");
        }
    }

    // Real-time data updates (simulating live data)
    function simulateRealTimeUpdates(): void {
        setInterval(() => {
            data = generateDummyTelemetryData();
            // Optionally update historical data too
            const newHistory = generateDummyHistoricalData();
            history = newHistory;
        }, 2000); // Update every 2 seconds
    }

    $: if (history.timestamps.length > 0) {
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

        // Start real-time simulation (comment out if not needed)
        simulateRealTimeUpdates();
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
    $: motorStatus = getMotorStatus(motor.temperature || 0);
    $: thermalStatus = getThermalStatus(motor.heatsink_temp || 0);
    $: powerStatus = getPowerStatus(motor.bus_power || 0);
</script>

<div class="space-y-6 p-6">
    <!-- Primary Motor Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="metric-card">
            <div class="metric-value text-green-400 text-2xl">
                {formatValue(motor.rpm, "RPM", 0)}
            </div>
            <div class="metric-label">Motor RPM</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-blue-400 text-2xl">
                {formatValue(motor.velocity, "km/h")}
            </div>
            <div class="metric-label">Velocity</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400 text-2xl">
                {formatValue(motor.temperature, "°C")}
            </div>
            <div class="metric-label">Motor Temperature</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-cyan-400 text-2xl">
                {formatValue(motor.heatsink_temp, "°C")}
            </div>
            <div class="metric-label">Heatsink Temperature</div>
        </div>
    </div>

    <!-- Phase Current and Bus Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue(motor.phase_current_b, "A")}
            </div>
            <div class="metric-label">Phase Current B</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-purple-400">
                {formatValue(motor.phase_current_c, "A")}
            </div>
            <div class="metric-label">Phase Current C</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-yellow-400">
                {formatValue(motor.bus_voltage, "V")}
            </div>
            <div class="metric-label">Bus Voltage</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-red-400">
                {formatValue(motor.bus_current, "A")}
            </div>
            <div class="metric-label">Bus Current</div>
        </div>

        <div class="metric-card">
            <div class="metric-value text-orange-400">
                {formatValue(motor.bus_power, "W", 0)}
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
                        ((motor.velocity || 0) / (motor.rpm || 1)) * 60,
                        "m/rev",
                        3
                    )}
                </div>
                <div class="text-sm text-gray-400">Distance per Revolution</div>
            </div>

            <div class="text-center">
                <div class="text-2xl font-bold text-green-400">
                    {formatValue(
                        (motor.bus_power || 0) / (motor.velocity || 1),
                        "W⋅h/km",
                        1
                    )}
                </div>
                <div class="text-sm text-gray-400">Power per Speed</div>
            </div>

            <div class="text-center">
                <div class="text-2xl font-bold text-purple-400">
                    {formatValue(
                        ((motor.phase_current_b || 0) +
                            (motor.phase_current_c || 0)) /
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
