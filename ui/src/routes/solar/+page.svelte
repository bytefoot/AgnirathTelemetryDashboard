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
    import type { MPPTFlags } from '$lib/store_types';

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
    let inputVoltageCanvas: HTMLCanvasElement;
    let outputPowerCanvas: HTMLCanvasElement;

    // Chart instances
    let inputVoltageChart: Chart;
    let outputPowerChart: Chart;

    const mpptNames = ['A', 'B', 'C', 'D'];

    type FlagItem = {
        key: keyof MPPTFlags;  // Ensures key must match SystemFlags properties
        label: string;
    };
    
    const flags: FlagItem[] = [
        { key: 'hw_overvolt', label: 'HW OV'},
        { key: 'hw_overcurrent', label: 'HW OC'},
        { key: 'under12v', label: '12V UV'},
        { key: 'low_array_power', label: 'LAP'},
        { key: 'battery_full', label: 'Batt Full'},
        { key: 'battery_low', label: 'Batt Low'},
        { key: 'mosfet_overheat', label: 'MOSFET'},
    ];

    // MPPT colors for charts
    const mpptColors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)}${unit}`;
    }

    function getStatusBorder(status: string): string {
        switch (status) {
            case "ok":
                return "border-green-500/30";
            case "warning":
                return "border-yellow-500/50";
            case "error":
                return "border-red-500/70";
            default:
                return "border-gray-500/30";
        }
    }

    function getStatusBg(status: string): string {
        switch (status) {
            case "ok":
                return "bg-green-500/5";
            case "warning":
                return "bg-yellow-500/5";
            case "error":
                return "bg-red-500/5";
            default:
                return "bg-gray-500/5";
        }
    }

    function createSingleLineChartConfig(
        title: string,
        yAxisLabel: string,
        dataType: "solar_input_voltage" | "solar_output_power"
    ): ChartConfiguration {
        return {
            type: "line",
            data: {
                labels: $globalStore.historic.Timestamps,
                datasets: [
                    {
                        label: title, // You can change this to "Net" or another label
                        data: $globalStore.historic[dataType],
                        borderColor: "#3b82f6", // Blue color (tailwind-like)
                        backgroundColor: "#3b82f620", // Blue with 20% opacity
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
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: yAxisLabel,
                            color: "#fff",
                        },
                        ticks: {
                            color: "#fff",
                        },
                        grid: {
                            color: "#374151", // Gray grid lines
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
                        text: title,
                        color: "#fff",
                    },
                },
            },
        };
    }

    function updateCharts(): void {
        if ($globalStore.historic.Timestamps.length === 0) return;

        if (inputVoltageChart) {
            inputVoltageChart.data.labels = $globalStore.historic.Timestamps;
            inputVoltageChart.data.datasets[0].data =
                $globalStore.historic.solar_input_voltage;
            inputVoltageChart.update("none");
        }

        if (outputPowerChart) {
            outputPowerChart.data.labels = $globalStore.historic.Timestamps;
            outputPowerChart.data.datasets[0].data =
                $globalStore.historic.solar_output_power;
            outputPowerChart.update("none");
        }
    }

    // Reactive statement to update charts when history changes
    $effect(() => {
        if ($globalStore.historic.Timestamps.length > 0) {
            updateCharts();
        }
    });

    // Calculate totals for summary
    const totalPower = $derived($globalStore.metric.mppts.reduce((sum, mppt) => sum + mppt.Output_Power, 0));
    const avgEfficiency = $derived($globalStore.metric.mppts.reduce((sum, mppt) => sum + mppt.efficiency, 0) / $globalStore.metric.mppts.length);
    // $: avgEfficiency = mpptData.reduce((sum, mppt) => sum + mppt.efficiency, 0) / mpptData.length;
    // $: activeUnits = mpptData.filter(mppt => mppt.status === 'ok').length;

    onMount(() => {
        // Create charts
        if (inputVoltageCanvas) {
            inputVoltageChart = new Chart(
                inputVoltageCanvas,
                createSingleLineChartConfig(
                    "MPPT Input Voltage vs Time",
                    "Input Voltage (V)",
                    "solar_input_voltage"
                )
            );
        }

        if (outputPowerCanvas) {
            outputPowerChart = new Chart(
                outputPowerCanvas,
                createSingleLineChartConfig(
                    "MPPT Output Power vs Time",
                    "Output Power (W)",
                    "solar_output_power"
                )
            );
        }

        return () => {
            // Cleanup charts
            inputVoltageChart?.destroy();
            outputPowerChart?.destroy();
        };
    });
</script>

<div class="dashboard-container">
    <!-- MPPT Overview Cards - Top Section -->
    <div class="mppt-overview-section">
        <!-- System Summary -->
        <div class="system-summary-card">
            <div class="summary-header">
                <h2 class="summary-title">☀️ Solar Array Status</h2>
                <div class="status-indicators">
                    {#each $globalStore.metric.mppts as mppt, mpptIndex}
                        <!-- <div class="status-dot {mppt.status === 'ok' ? 'dot-ok' : mppt.status === 'warning' ? 'dot-warning' : 'dot-error'}"  -->
                        <div
                            class="status-dot {'dot-ok'}"
                            style="background-color: {mpptColors[mpptIndex]}"
                        ></div>
                    {/each}
                </div>
            </div>
            <div class="summary-stats">
                <div class="stat-item">
                    <div class="stat-value text-yellow-400">{formatValue(totalPower, 'W', 0)}</div>
                    <div class="stat-label">Total Power</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value text-green-400">{formatValue(avgEfficiency, '%')}</div>
                    <div class="stat-label">Avg Efficiency</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value text-blue-400">N/A</div>
                    <div class="stat-label">Active Units</div>
                </div>
            </div>
        </div>

        <!-- MPPT Units Grid -->
        <div class="mppt-grid">
            {#each $globalStore.metric.mppts as mppt, mpptIndex}
                <div
                    class="mppt-card-modern {getStatusBorder('ok')} {getStatusBg('ok')}"
                >
                    <!-- MPPT Header -->
                    <div class="mppt-header">
                        <div class="mppt-title-section">
                            <h3
                                class="mppt-name"
                                style="color: {mpptColors[mpptIndex]}"
                            >
                                {"MPPT " + mpptNames[mpptIndex]}
                            </h3>
                            <div class="power-display">
                                <span class="power-value text-yellow-400"
                                    >{formatValue(mppt.Output_Power, "", 0)}</span
                                >
                                <span class="power-unit">W</span>
                            </div>
                        </div>
        
                        <!-- NEW: Temperature Section -->
                        <div class="temperature-section">
                            <div class="temp-item">
                                <span class="temp-label">MOSFET</span>
                                <span class="temp-value text-orange-400">
                                    {formatValue(mppt.Mosfet_Temperature, "°C")}
                                </span>
                            </div>
                            <div class="temp-item">
                                <span class="temp-label">MPPT</span>
                                <span class="temp-value text-red-400">
                                    {formatValue(mppt.MPPT_Temperature, "°C")}
                                </span>
                            </div>
                        </div>
        
                        <div class="efficiency-circle circle-ok">
                            <span class="efficiency-text"
                                >{formatValue(mppt.efficiency, "", 1)}%</span
                            >
                        </div>
                    </div>
        
                    <!-- NEW: MPPT Flags -->
                    <div class="mppt-flags">
                        {#each flags as flag}
                            <div class="flag-indicator {mppt.flags[flag.key] ? 'flag-active' : 'flag-inactive'}">
                                <div class="flag-dot"></div>
                                <span class="flag-text">{flag.label}</span>
                            </div>
                        {/each}
                    </div>
        
                    <!-- Metrics Grid (unchanged) -->
                    <div class="metrics-grid">
                        <!-- Input Column -->
                        <div class="metric-column">
                            <div class="column-label">INPUT</div>
                            <div class="metric-row">
                                <span class="metric-icon">⚡</span>
                                <div class="metric-data">
                                    <span class="metric-value text-blue-400"
                                        >{formatValue(mppt.Input_Voltage, "")}</span
                                    >
                                    <span class="metric-unit">V</span>
                                </div>
                            </div>
                            <div class="metric-row">
                                <span class="metric-icon">🔌</span>
                                <div class="metric-data">
                                    <span class="metric-value text-cyan-400"
                                        >{formatValue(mppt.Input_Current, "")}</span
                                    >
                                    <span class="metric-unit">A</span>
                                </div>
                            </div>
                        </div>
        
                        <!-- Output Column -->
                        <div class="metric-column">
                            <div class="column-label">OUTPUT</div>
                            <div class="metric-row">
                                <span class="metric-icon">⚡</span>
                                <div class="metric-data">
                                    <span class="metric-value text-green-400"
                                        >{formatValue(mppt.Output_Voltage, "")}</span
                                    >
                                    <span class="metric-unit">V</span>
                                </div>
                            </div>
                            <div class="metric-row">
                                <span class="metric-icon">🔌</span>
                                <div class="metric-data">
                                    <span class="metric-value text-emerald-400"
                                        >{formatValue(mppt.Output_Current, "")}</span
                                    >
                                    <span class="metric-unit">A</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
        <div class="chart-container">
            <canvas bind:this={inputVoltageCanvas} class="chart-canvas"
            ></canvas>
        </div>

        <div class="chart-container">
            <canvas bind:this={outputPowerCanvas} class="chart-canvas"></canvas>
        </div>
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";

    .dashboard-container {
        @apply p-4 space-y-6 bg-gray-900 min-h-screen;
    }

    .mppt-overview-section {
        @apply space-y-4;
    }

    .system-summary-card {
        @apply bg-gray-800 rounded-xl p-4 border border-gray-700;
    }

    .summary-header {
        @apply flex items-center justify-between mb-3;
    }

    .summary-title {
        @apply text-lg font-bold text-white;
    }

    .status-indicators {
        @apply flex gap-2;
    }

    .status-dot {
        @apply w-3 h-3 rounded-full;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-dot.dot-warning,
    .status-dot.dot-error {
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .summary-stats {
        @apply grid grid-cols-3 gap-4;
    }

    .stat-item {
        @apply text-center;
    }

    .stat-value {
        @apply text-xl font-bold;
    }

    .stat-label {
        @apply text-xs text-gray-400 mt-1;
    }

    .mppt-grid {
        @apply grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4;
    }

    .mppt-card-modern {
        @apply bg-gray-800 rounded-xl p-4 border transition-all duration-300 hover:scale-105 relative overflow-hidden;
    }

    .mppt-header {
        @apply flex items-start justify-between mb-4;
    }

    .mppt-title-section {
        @apply flex-1;
    }

    .mppt-name {
        @apply font-bold text-sm mb-1;
    }

    .power-display {
        @apply flex items-baseline gap-1;
    }

    .power-value {
        @apply text-2xl font-bold;
    }

    .power-unit {
        @apply text-sm text-gray-400;
    }

    .efficiency-circle {
        @apply w-12 h-12 rounded-full border-2 flex items-center justify-center;
    }

    .efficiency-circle.circle-ok {
        @apply border-green-500 bg-green-500/10;
    }

    .efficiency-circle.circle-warning {
        @apply border-yellow-500 bg-yellow-500/10;
    }

    .efficiency-circle.circle-error {
        @apply border-red-500 bg-red-500/10;
    }

    .efficiency-text {
        @apply text-xs font-bold text-white;
    }

    .metrics-grid {
        @apply grid grid-cols-2 gap-4 mb-4;
    }

    .metric-column {
        @apply space-y-2;
    }

    .column-label {
        @apply text-xs font-semibold text-gray-400 border-b border-gray-600 pb-1;
    }

    .metric-row {
        @apply flex items-center gap-2;
    }

    .metric-icon {
        @apply text-sm;
    }

    .metric-data {
        @apply flex items-baseline gap-1;
    }

    .metric-value {
        @apply font-bold text-sm;
    }

    .metric-unit {
        @apply text-xs text-gray-400;
    }

    .charts-section {
        @apply grid grid-cols-1 xl:grid-cols-2 gap-6;
    }

    .chart-container {
        @apply bg-gray-800 rounded-xl p-4 border border-gray-700;
    }

    .chart-canvas {
        @apply w-full h-80;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .mppt-grid {
            @apply grid-cols-1;
        }

        .charts-section {
            @apply grid-cols-1;
        }

        .summary-stats {
            @apply grid-cols-1 gap-2;
        }

        .metrics-grid {
            @apply grid-cols-1 gap-2;
        }
    }

    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

/* NEW: Temperature Section Styles */
.temperature-section {
        @apply flex gap-1 mx-2 mr-6.5;
    }

    .temp-item {
        @apply flex flex-col items-center;
    }

    .temp-label {
        @apply text-xs text-gray-400 font-medium;
    }

    .temp-value {
        @apply text-sm font-bold;
    }

    /* NEW: MPPT Flags Styles */
    .mppt-flags {
        @apply flex flex-wrap gap-1 mb-3 px-1;
    }

    .flag-indicator {
        @apply flex items-center gap-1 px-2 py-1 rounded-md text-xs transition-colors;
    }

    .flag-active {
        @apply bg-red-900/30 border border-red-500/50;
    }

    .flag-inactive {
        @apply bg-gray-800/50 border border-gray-600/30;
    }

    .flag-dot {
        @apply w-2 h-2 rounded-full flex-shrink-0;
    }

    .flag-active .flag-dot {
        @apply bg-red-400;
    }

    .flag-inactive .flag-dot {
        @apply bg-gray-500;
    }

    .flag-text {
        @apply text-gray-300 font-medium leading-none;
    }

    .flag-active .flag-text {
        @apply text-red-300;
    }

    /* MODIFY existing mppt-header to accommodate new layout */
    .mppt-header {
        @apply flex items-start justify-between mb-3; /* reduced margin bottom */
    }
</style>
