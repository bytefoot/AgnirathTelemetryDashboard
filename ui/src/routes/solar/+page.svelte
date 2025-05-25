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
    interface MPPTData {
        id: number;
        name: string;
        inputVoltage: number;
        outputVoltage: number;
        inputCurrent: number;
        outputCurrent: number;
        outputPower: number;
        efficiency: number;
        status: "ok" | "warning" | "error";
        color: string;
    }

    interface HistoricalMPPTData {
        timestamps: string[];
        inputVoltage: { [key: number]: number[] };
        outputPower: { [key: number]: number[] };
    }

    // Canvas element references
    let inputVoltageCanvas: HTMLCanvasElement;
    let outputPowerCanvas: HTMLCanvasElement;

    // Chart instances
    let inputVoltageChart: Chart;
    let outputPowerChart: Chart;

    // MPPT colors for charts
    const mpptColors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

    // Dummy MPPT data
    let mpptData: MPPTData[] = [
        {
            id: 1,
            name: "MPPT 1",
            inputVoltage: 24.2,
            outputVoltage: 48.1,
            inputCurrent: 8.5,
            outputCurrent: 4.2,
            outputPower: 202,
            efficiency: 94.2,
            status: "ok",
            color: mpptColors[0],
        },
        {
            id: 2,
            name: "MPPT 2",
            inputVoltage: 23.8,
            outputVoltage: 48.0,
            inputCurrent: 7.9,
            outputCurrent: 3.9,
            outputPower: 187,
            efficiency: 93.8,
            status: "ok",
            color: mpptColors[1],
        },
        {
            id: 3,
            name: "MPPT 3",
            inputVoltage: 22.1,
            outputVoltage: 47.8,
            inputCurrent: 6.2,
            outputCurrent: 2.8,
            outputPower: 134,
            efficiency: 92.1,
            status: "warning",
            color: mpptColors[2],
        },
        {
            id: 4,
            name: "MPPT 4",
            inputVoltage: 21.5,
            outputVoltage: 47.9,
            inputCurrent: 5.8,
            outputCurrent: 2.6,
            outputPower: 125,
            efficiency: 91.4,
            status: "ok",
            color: mpptColors[3],
        },
    ];

    let history: HistoricalMPPTData = {
        timestamps: [],
        inputVoltage: { 1: [], 2: [], 3: [], 4: [] },
        outputPower: { 1: [], 2: [], 3: [], 4: [] },
    };

    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)}${unit}`;
    }

    function getStatusColor(status: string): string {
        switch (status) {
            case "ok": return "text-green-400";
            case "warning": return "text-yellow-400";
            case "error": return "text-red-400";
            default: return "text-gray-400";
        }
    }

    function getStatusBorder(status: string): string {
        switch (status) {
            case "ok": return "border-green-500/30";
            case "warning": return "border-yellow-500/50";
            case "error": return "border-red-500/70";
            default: return "border-gray-500/30";
        }
    }

    function getStatusBg(status: string): string {
        switch (status) {
            case "ok": return "bg-green-500/5";
            case "warning": return "bg-yellow-500/5";
            case "error": return "bg-red-500/5";
            default: return "bg-gray-500/5";
        }
    }

    function generateHistoricalData(): void {
        const now = new Date();
        const timestamps: string[] = [];
        const inputVoltageData: { [key: number]: number[] } = { 1: [], 2: [], 3: [], 4: [] };
        const outputPowerData: { [key: number]: number[] } = { 1: [], 2: [], 3: [], 4: [] };

        for (let i = 59; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60000);
            timestamps.push(time.toLocaleTimeString());

            // Generate data for each MPPT
            mpptData.forEach((mppt) => {
                const baseVoltage = 20 + mppt.id * 2;
                const basePower = 100 + mppt.id * 50;
                
                inputVoltageData[mppt.id].push(
                    baseVoltage + Math.sin(i / 10) * 3 + Math.random() * 2
                );
                outputPowerData[mppt.id].push(
                    basePower + Math.sin(i / 8) * 30 + Math.random() * 20
                );
            });
        }

        history = {
            timestamps,
            inputVoltage: inputVoltageData,
            outputPower: outputPowerData,
        };
    }

    function createMultiLineChartConfig(
        title: string,
        yAxisLabel: string,
        dataType: "inputVoltage" | "outputPower"
    ): ChartConfiguration {
        const datasets = mpptData.map((mppt) => ({
            label: mppt.name,
            data: history[dataType][mppt.id],
            borderColor: mppt.color,
            backgroundColor: mppt.color + "20",
            borderWidth: 2,
            fill: false,
            tension: 0.1,
        }));

        return {
            type: "line",
            data: {
                labels: history.timestamps,
                datasets: datasets,
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
                        text: title,
                        color: "#fff",
                    },
                },
            },
        };
    }

    function updateCharts(): void {
        if (history.timestamps.length === 0) return;

        if (inputVoltageChart) {
            inputVoltageChart.data.labels = history.timestamps;
            mpptData.forEach((mppt, index) => {
                inputVoltageChart.data.datasets[index].data = history.inputVoltage[mppt.id];
            });
            inputVoltageChart.update("none");
        }

        if (outputPowerChart) {
            outputPowerChart.data.labels = history.timestamps;
            mpptData.forEach((mppt, index) => {
                outputPowerChart.data.datasets[index].data = history.outputPower[mppt.id];
            });
            outputPowerChart.update("none");
        }
    }

    function updateLiveData(): void {
        // Update MPPT data
        mpptData = mpptData.map((mppt) => ({
            ...mppt,
            inputVoltage: mppt.inputVoltage + (Math.random() - 0.5) * 0.5,
            outputVoltage: mppt.outputVoltage + (Math.random() - 0.5) * 0.2,
            inputCurrent: mppt.inputCurrent + (Math.random() - 0.5) * 0.3,
            outputCurrent: mppt.outputCurrent + (Math.random() - 0.5) * 0.2,
            outputPower: mppt.outputPower + (Math.random() - 0.5) * 10,
            efficiency: Math.max(85, Math.min(98, mppt.efficiency + (Math.random() - 0.5) * 0.5)),
        }));

        // Add new data points to history
        const newTimestamp = new Date().toLocaleTimeString();
        const newInputVoltage: { [key: number]: number[] } = { 1: [], 2: [], 3: [], 4: [] };
        const newOutputPower: { [key: number]: number[] } = { 1: [], 2: [], 3: [], 4: [] };

        mpptData.forEach((mppt) => {
            newInputVoltage[mppt.id] = [
                ...history.inputVoltage[mppt.id].slice(-59),
                mppt.inputVoltage,
            ];
            newOutputPower[mppt.id] = [
                ...history.outputPower[mppt.id].slice(-59),
                mppt.outputPower,
            ];
        });

        history = {
            timestamps: [...history.timestamps.slice(-59), newTimestamp],
            inputVoltage: newInputVoltage,
            outputPower: newOutputPower,
        };
    }

    // Reactive statement to update charts when history changes
    $: if (history.timestamps.length > 0) {
        updateCharts();
    }

    // Calculate totals for summary
    $: totalPower = mpptData.reduce((sum, mppt) => sum + mppt.outputPower, 0);
    $: avgEfficiency = mpptData.reduce((sum, mppt) => sum + mppt.efficiency, 0) / mpptData.length;
    $: activeUnits = mpptData.filter(mppt => mppt.status === 'ok').length;

    onMount(() => {
        generateHistoricalData();

        // Create charts
        if (inputVoltageCanvas) {
            inputVoltageChart = new Chart(
                inputVoltageCanvas,
                createMultiLineChartConfig(
                    "MPPT Input Voltage vs Time",
                    "Input Voltage (V)",
                    "inputVoltage"
                )
            );
        }

        if (outputPowerCanvas) {
            outputPowerChart = new Chart(
                outputPowerCanvas,
                createMultiLineChartConfig(
                    "MPPT Output Power vs Time",
                    "Output Power (W)",
                    "outputPower"
                )
            );
        }

        // Set up live data updates
        const interval = setInterval(updateLiveData, 3000);

        return () => {
            clearInterval(interval);
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
                    {#each mpptData as mppt}
                        <div class="status-dot {mppt.status === 'ok' ? 'dot-ok' : mppt.status === 'warning' ? 'dot-warning' : 'dot-error'}" 
                             style="background-color: {mppt.color}"></div>
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
                    <div class="stat-value text-blue-400">{activeUnits}/4</div>
                    <div class="stat-label">Active Units</div>
                </div>
            </div>
        </div>

        <!-- MPPT Units Grid -->
        <div class="mppt-grid">
            {#each mpptData as mppt}
                <div class="mppt-card-modern {getStatusBorder(mppt.status)} {getStatusBg(mppt.status)}">
                    <!-- MPPT Header -->
                    <div class="mppt-header">
                        <div class="mppt-title-section">
                            <h3 class="mppt-name" style="color: {mppt.color}">{mppt.name}</h3>
                            <div class="power-display">
                                <span class="power-value text-yellow-400">{formatValue(mppt.outputPower, '', 0)}</span>
                                <span class="power-unit">W</span>
                            </div>
                        </div>
                        <div class="efficiency-circle {mppt.status === 'ok' ? 'circle-ok' : mppt.status === 'warning' ? 'circle-warning' : 'circle-error'}">
                            <span class="efficiency-text">{formatValue(mppt.efficiency, '', 1)}%</span>
                        </div>
                    </div>

                    <!-- Metrics Grid -->
                    <div class="metrics-grid">
                        <!-- Input Column -->
                        <div class="metric-column">
                            <div class="column-label">INPUT</div>
                            <div class="metric-row">
                                <span class="metric-icon">⚡</span>
                                <div class="metric-data">
                                    <span class="metric-value text-blue-400">{formatValue(mppt.inputVoltage, '')}</span>
                                    <span class="metric-unit">V</span>
                                </div>
                            </div>
                            <div class="metric-row">
                                <span class="metric-icon">🔌</span>
                                <div class="metric-data">
                                    <span class="metric-value text-cyan-400">{formatValue(mppt.inputCurrent, '')}</span>
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
                                    <span class="metric-value text-green-400">{formatValue(mppt.outputVoltage, '')}</span>
                                    <span class="metric-unit">V</span>
                                </div>
                            </div>
                            <div class="metric-row">
                                <span class="metric-icon">🔌</span>
                                <div class="metric-data">
                                    <span class="metric-value text-emerald-400">{formatValue(mppt.outputCurrent, '')}</span>
                                    <span class="metric-unit">A</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Status Bar -->
                    <div class="status-bar">
                        <div class="status-indicator-bar {mppt.status === 'ok' ? 'bar-ok' : mppt.status === 'warning' ? 'bar-warning' : 'bar-error'}">
                            <div class="status-fill" style="width: {mppt.efficiency}%; background: linear-gradient(90deg, {mppt.color}40, {mppt.color})"></div>
                        </div>
                        <span class="status-text {getStatusColor(mppt.status)}">{mppt.status.toUpperCase()}</span>
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
        <div class="chart-container">
            <canvas bind:this={inputVoltageCanvas} class="chart-canvas"></canvas>
        </div>

        <div class="chart-container">
            <canvas bind:this={outputPowerCanvas} class="chart-canvas"></canvas>
        </div>
    </div>
</div>

<style lang='postcss'>
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

    .status-dot.dot-warning, .status-dot.dot-error {
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

    .status-bar {
        @apply flex items-center gap-2;
    }

    .status-indicator-bar {
        @apply flex-1 h-2 bg-gray-700 rounded-full overflow-hidden;
    }

    .status-fill {
        @apply h-full transition-all duration-500;
    }

    .status-text {
        @apply text-xs font-bold;
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
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: .5;
        }
    }
</style>