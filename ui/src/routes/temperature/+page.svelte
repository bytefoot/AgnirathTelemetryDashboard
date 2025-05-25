<script lang="ts">
    import { onMount } from "svelte";

    // TypeScript interfaces
    interface TemperatureReading {
        id: string;
        name: string;
        temperature: number;
        warningThreshold: number;
        errorThreshold: number;
        unit: string;
        location: string;
        category: "motor" | "battery" | "controller" | "ambient" | "solar";
    }

    // Temperature data with realistic thresholds
    let temperatureData: TemperatureReading[] = [
        {
            id: "battery_1",
            name: "Battery Pack Core",
            temperature: 28.3,
            warningThreshold: 35,
            errorThreshold: 45,
            unit: "°C",
            location: "Battery Bay",
            category: "battery",
        },
        {
            id: "battery_2",
            name: "Battery BMS",
            temperature: 31.7,
            warningThreshold: 40,
            errorThreshold: 50,
            unit: "°C",
            location: "Battery Bay",
            category: "battery",
        },
        {
            id: "battery_3",
            name: "Cell Block 1",
            temperature: 29.1,
            warningThreshold: 35,
            errorThreshold: 45,
            unit: "°C",
            location: "Battery Bay",
            category: "battery",
        },
        {
            id: "battery_4",
            name: "Cell Block 2",
            temperature: 30.4,
            warningThreshold: 35,
            errorThreshold: 45,
            unit: "°C",
            location: "Battery Bay",
            category: "battery",
        },
        {
            id: "solar_1",
            name: "MPPT 1",
            temperature: 51.3,
            warningThreshold: 60,
            errorThreshold: 70,
            unit: "°C",
            location: "Solar Array",
            category: "solar",
        },
        {
            id: "solar_2",
            name: "MPPT 2",
            temperature: 49.7,
            warningThreshold: 60,
            errorThreshold: 70,
            unit: "°C",
            location: "Solar Array",
            category: "solar",
        },
        {
            id: "solar_3",
            name: "MPPT 3",
            temperature: 53.1,
            warningThreshold: 60,
            errorThreshold: 70,
            unit: "°C",
            location: "Solar Array",
            category: "solar",
        },
        {
            id: "solar_4",
            name: "MPPT 4",
            temperature: 48.9,
            warningThreshold: 60,
            errorThreshold: 70,
            unit: "°C",
            location: "Solar Array",
            category: "solar",
        },
        {
            id: "motor_1",
            name: "Motor Controller",
            temperature: 68.5,
            warningThreshold: 75,
            errorThreshold: 85,
            unit: "°C",
            location: "Drive Unit",
            category: "motor",
        },
        {
            id: "motor_2",
            name: "Motor Windings",
            temperature: 72.1,
            warningThreshold: 80,
            errorThreshold: 90,
            unit: "°C",
            location: "Drive Unit",
            category: "motor",
        },
        {
            id: "controller_1",
            name: "Main Controller",
            temperature: 45.2,
            warningThreshold: 55,
            errorThreshold: 65,
            unit: "°C",
            location: "Electronics Bay",
            category: "controller",
        },
        {
            id: "controller_2",
            name: "Power Distribution",
            temperature: 42.8,
            warningThreshold: 50,
            errorThreshold: 60,
            unit: "°C",
            location: "Electronics Bay",
            category: "controller",
        },
        {
            id: "ambient_1",
            name: "Cabin Interior",
            temperature: 24.1,
            warningThreshold: 35,
            errorThreshold: 45,
            unit: "°C",
            location: "Interior",
            category: "ambient",
        },
        {
            id: "ambient_2",
            name: "External Air",
            temperature: 21.5,
            warningThreshold: 40,
            errorThreshold: 50,
            unit: "°C",
            location: "Exterior",
            category: "ambient",
        },
    ];

    function formatValue(
        value: number | undefined,
        unit: string = "",
        decimals: number = 1
    ): string {
        if (typeof value !== "number") return "N/A";
        return `${value.toFixed(decimals)}${unit}`;
    }

    function getTemperatureStatus(reading: TemperatureReading): "ok" | "warning" | "error" {
        if (reading.temperature >= reading.errorThreshold) return "error";
        if (reading.temperature >= reading.warningThreshold) return "warning";
        return "ok";
    }

    function getTemperatureColor(reading: TemperatureReading): string {
        const status = getTemperatureStatus(reading);
        switch (status) {
            case "ok": return "text-green-400";
            case "warning": return "text-orange-400";
            case "error": return "text-red-400";
            default: return "text-gray-400";
        }
    }

    function getTemperatureGradient(reading: TemperatureReading): string {
        const status = getTemperatureStatus(reading);
        switch (status) {
            case "ok": return "from-blue-500 to-green-500";
            case "warning": return "from-yellow-500 to-orange-500";
            case "error": return "from-orange-500 to-red-600";
            default: return "from-gray-500 to-gray-600";
        }
    }

    function getTemperatureBorder(reading: TemperatureReading): string {
        const status = getTemperatureStatus(reading);
        switch (status) {
            case "ok": return "border-green-500/30";
            case "warning": return "border-orange-500/50";
            case "error": return "border-red-500/70";
            default: return "border-gray-500/30";
        }
    }

    function getCategoryIcon(category: string): string {
        switch (category) {
            case "motor": return "⚡";
            case "battery": return "🔋";
            case "controller": return "🖥️";
            case "solar": return "☀️";
            case "ambient": return "🌡️";
            default: return "📊";
        }
    }

    function getCategoryColor(category: string): string {
        switch (category) {
            case "motor": return "text-blue-400";
            case "battery": return "text-green-400";
            case "controller": return "text-purple-400";
            case "solar": return "text-yellow-400";
            case "ambient": return "text-cyan-400";
            default: return "text-gray-400";
        }
    }

    function getCategoryBg(category: string): string {
        switch (category) {
            case "motor": return "bg-blue-500/10";
            case "battery": return "bg-green-500/10";
            case "controller": return "bg-purple-500/10";
            case "solar": return "bg-yellow-500/10";
            case "ambient": return "bg-cyan-500/10";
            default: return "bg-gray-500/10";
        }
    }

    function getTemperaturePercentage(reading: TemperatureReading): number {
        const range = reading.errorThreshold - 0;
        const current = Math.max(0, reading.temperature);
        return Math.min(100, (current / range) * 100);
    }

    function updateLiveData(): void {
        temperatureData = temperatureData.map((reading) => ({
            ...reading,
            temperature: Math.max(0, reading.temperature + (Math.random() - 0.5) * 2),
        }));
    }

    // Group temperatures by category
    $: groupedTemperatures = temperatureData.reduce((acc, reading) => {
        if (!acc[reading.category]) {
            acc[reading.category] = [];
        }
        acc[reading.category].push(reading);
        return acc;
    }, {} as Record<string, TemperatureReading[]>);

    // Get overall system status
    $: systemStatus = (() => {
        const errorCount = temperatureData.filter(r => getTemperatureStatus(r) === "error").length;
        const warningCount = temperatureData.filter(r => getTemperatureStatus(r) === "warning").length;
        
        if (errorCount > 0) return "error";
        if (warningCount > 0) return "warning";
        return "ok";
    })();

    onMount(() => {
        // Set up live data updates
        const interval = setInterval(updateLiveData, 4000);

        return () => {
            clearInterval(interval);
        };
    });
</script>

<div class="dashboard-container">
    <!-- Header Stats -->
    <div class="stats-header">
        <div class="system-status-card {systemStatus === 'ok' ? 'status-ok' : systemStatus === 'warning' ? 'status-warning' : 'status-error'}">
            <div class="status-indicator">
                <div class="status-dot {systemStatus === 'ok' ? 'dot-ok' : systemStatus === 'warning' ? 'dot-warning' : 'dot-error'}"></div>
                <span class="status-text">System Status</span>
            </div>
            <div class="status-counts">
                <div class="count-item">
                    <span class="count-value text-green-400">{temperatureData.filter(r => getTemperatureStatus(r) === "ok").length}</span>
                    <span class="count-label">OK</span>
                </div>
                <div class="count-item">
                    <span class="count-value text-orange-400">{temperatureData.filter(r => getTemperatureStatus(r) === "warning").length}</span>
                    <span class="count-label">WARN</span>
                </div>
                <div class="count-item">
                    <span class="count-value text-red-400">{temperatureData.filter(r => getTemperatureStatus(r) === "error").length}</span>
                    <span class="count-label">CRIT</span>
                </div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value text-red-400">{formatValue(Math.max(...temperatureData.map(r => r.temperature)), "°C")}</div>
            <div class="stat-label">Peak</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value text-blue-400">{formatValue(temperatureData.reduce((sum, r) => sum + r.temperature, 0) / temperatureData.length, "°C")}</div>
            <div class="stat-label">Average</div>
        </div>
    </div>

    <!-- Temperature Grid -->
    <div class="temp-grid">
        {#each Object.entries(groupedTemperatures) as [category, readings]}
            <div class="category-panel {getCategoryBg(category)}">
                <div class="category-header">
                    <span class="category-icon">{getCategoryIcon(category)}</span>
                    <span class="category-title {getCategoryColor(category)}">{category.toUpperCase()}</span>
                    <div class="category-stats">
                        {#each readings as reading}
                            <div class="mini-indicator {getTemperatureStatus(reading) === 'ok' ? 'mini-ok' : getTemperatureStatus(reading) === 'warning' ? 'mini-warning' : 'mini-error'}"></div>
                        {/each}
                    </div>
                </div>
                
                <div class="sensors-grid">
                    {#each readings as reading}
                        <div class="sensor-card {getTemperatureBorder(reading)}">
                            <div class="sensor-header">
                                <span class="sensor-name">{reading.name.replace(/\s+/g, '\n')}</span>
                                <div class="status-indicator-small {getTemperatureStatus(reading) === 'ok' ? 'status-ok-small' : getTemperatureStatus(reading) === 'warning' ? 'status-warning-small' : 'status-error-small'}"></div>
                            </div>
                            
                            <div class="temp-display bg-gradient-to-br {getTemperatureGradient(reading)}">
                                <span class="temp-value">{formatValue(reading.temperature, '')}</span>
                                <span class="temp-unit">°C</span>
                            </div>
                            
                            <div class="temp-bar-container">
                                <div class="temp-bar-bg">
                                    <div class="temp-bar-fill bg-gradient-to-r {getTemperatureGradient(reading)}" 
                                         style="width: {getTemperaturePercentage(reading)}%"></div>
                                    <div class="threshold warning-threshold" 
                                         style="left: {(reading.warningThreshold / reading.errorThreshold) * 100}%"></div>
                                    <div class="threshold error-threshold" 
                                         style="left: 100%"></div>
                                </div>
                            </div>
                            
                            <div class="thresholds">
                                <span class="threshold-text text-orange-300">{reading.warningThreshold}°</span>
                                <span class="threshold-text text-red-300">{reading.errorThreshold}°</span>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/each}
    </div>
</div>

<style lang='postcss'>
    @reference "tailwindcss";

    .dashboard-container {
        @apply p-4 space-y-4 bg-gray-900 min-h-screen;
    }

    .stats-header {
        @apply grid grid-cols-1 md:grid-cols-3 gap-4;
    }

    .system-status-card {
        @apply rounded-xl p-4 border-2 transition-all duration-300;
    }

    .system-status-card.status-ok {
        @apply border-green-500 bg-green-500/5;
    }

    .system-status-card.status-warning {
        @apply border-orange-500 bg-orange-500/5;
    }

    .system-status-card.status-error {
        @apply border-red-500 bg-red-500/5;
        animation: critical-pulse 2s ease-in-out infinite;
    }

    .status-indicator {
        @apply flex items-center gap-2 mb-3;
    }

    .status-dot {
        @apply w-3 h-3 rounded-full;
    }

    .status-dot.dot-ok {
        @apply bg-green-500;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-dot.dot-warning {
        @apply bg-orange-500;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-dot.dot-error {
        @apply bg-red-500;
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-text {
        @apply text-white font-semibold text-sm;
    }

    .status-counts {
        @apply flex justify-between;
    }

    .count-item {
        @apply text-center;
    }

    .count-value {
        @apply text-xl font-bold block;
    }

    .count-label {
        @apply text-xs text-gray-400;
    }

    .stat-card {
        @apply bg-gray-800 rounded-xl p-4 text-center;
    }

    .stat-value {
        @apply text-2xl font-bold;
    }

    .stat-label {
        @apply text-sm text-gray-400 mt-1;
    }

    .temp-grid {
        @apply grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4;
    }

    .category-panel {
        @apply rounded-xl p-4 border border-gray-700;
    }

    .category-header {
        @apply flex items-center justify-between mb-3;
    }

    .category-icon {
        @apply text-lg;
    }

    .category-title {
        @apply font-bold text-sm flex-1 ml-2;
    }

    .category-stats {
        @apply flex gap-1;
    }

    .mini-indicator {
        @apply w-2 h-2 rounded-full;
    }

    .mini-indicator.mini-ok {
        @apply bg-green-500;
    }

    .mini-indicator.mini-warning {
        @apply bg-orange-500;
    }

    .mini-indicator.mini-error {
        @apply bg-red-500;
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .sensors-grid {
        @apply grid grid-cols-2 gap-3;
    }

    .sensor-card {
        @apply bg-gray-800 rounded-lg p-3 border transition-all duration-300 hover:scale-105;
    }

    .sensor-header {
        @apply flex items-start justify-between mb-2;
    }

    .sensor-name {
        @apply text-xs text-gray-300 font-medium leading-tight flex-1 whitespace-pre-line;
    }

    .status-indicator-small {
        @apply w-2 h-2 rounded-full flex-shrink-0 ml-1;
    }

    .status-indicator-small.status-ok-small {
        @apply bg-green-500;
    }

    .status-indicator-small.status-warning-small {
        @apply bg-orange-500;
    }

    .status-indicator-small.status-error-small {
        @apply bg-red-500;
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .temp-display {
        @apply rounded-md p-2 text-center mb-2 shadow-inner;
    }

    .temp-value {
        @apply text-lg font-bold text-white;
    }

    .temp-unit {
        @apply text-xs text-white/80 ml-1;
    }

    .temp-bar-container {
        @apply mb-2;
    }

    .temp-bar-bg {
        @apply w-full h-1.5 bg-gray-700 rounded-full relative overflow-hidden;
    }

    .temp-bar-fill {
        @apply h-full rounded-full transition-all duration-500 ease-out;
    }

    .threshold {
        @apply absolute top-0 w-0.5 h-full z-10;
    }

    .threshold.warning-threshold {
        @apply bg-orange-400;
    }

    .threshold.error-threshold {
        @apply bg-red-400;
    }

    .thresholds {
        @apply flex justify-between;
    }

    .threshold-text {
        @apply text-xs font-medium;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: .5;
        }
    }

    @keyframes critical-pulse {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
        }
        50% {
            box-shadow: 0 0 0 8px rgba(239, 68, 68, 0.1);
        }
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .sensors-grid {
            @apply grid-cols-1;
        }
        
        .temp-grid {
            @apply grid-cols-1;
        }
    }
</style>