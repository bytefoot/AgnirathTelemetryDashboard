<script lang="ts">
    import { onMount } from "svelte";
    import { globalStore } from "$lib/store";
    import type { TelemetryData } from "$lib/store_types";

    const mpptNames = ['A', 'B', 'C', 'D'];
    const MotorTempKeys: (keyof TelemetryData['metric'])[] = ['Motor_Temp', 'HeatSink_Temp', 'DSP_Board_Temp',]

    // Utility functions
    function formatValue(
        value: number,
        unit: string = "",
        decimals: number = 1
    ): string {
        return `${value.toFixed(decimals)}${unit}`;
    }

    function getFlagStatus(
        flags: Record<string, boolean>
    ): "ok" | "warning" | "error" {
        const errorFlags = Object.values(flags).filter(Boolean);
        if (errorFlags.length > 2) return "error";
        if (errorFlags.length > 0) return "warning";
        return "ok";
    }

    function getStatusColor(status: "ok" | "warning" | "error"): string {
        switch (status) {
            case "ok":
                return "text-green-400";
            case "warning":
                return "text-orange-400";
            case "error":
                return "text-red-400";
            default:
                return "text-gray-400";
        }
    }

    function getStatusBg(status: "ok" | "warning" | "error"): string {
        switch (status) {
            case "ok":
                return "bg-green-500/10 border-green-500/30";
            case "warning":
                return "bg-orange-500/10 border-orange-500/50";
            case "error":
                return "bg-red-500/10 border-red-500/70";
            default:
                return "bg-gray-500/10 border-gray-500/30";
        }
    }

    function getGasLevelStatus(
        value: number,
        gasType: string
    ): "ok" | "warning" | "error" {
        // These are example thresholds - adjust based on your safety requirements
        const thresholds = {
            CO: { warning: 10, error: 25 },
            CH4: { warning: 100, error: 500 },
            NH3: { warning: 25, error: 50 },
            NO2: { warning: 3, error: 10 },
            O2: { warning: 16, error: 14 }, // O2 is inverted - lower is worse
            CO2: { warning: 1000, error: 5000 },
        };

        const gasKey = gasType
            .replace("Cabin_", "")
            .replace("_Content", "") as keyof typeof thresholds;
        const threshold = thresholds[gasKey];

        if (!threshold) return "ok";

        if (gasKey === "O2") {
            // Oxygen - lower values are worse
            if (value <= threshold.error) return "error";
            if (value <= threshold.warning) return "warning";
            return "ok";
        } else {
            // Other gases - higher values are worse
            if (value >= threshold.error) return "error";
            if (value >= threshold.warning) return "warning";
            return "ok";
        }
    }

    function formatFlagName(key: string): string {
        return key
            .replace(/_/g, " ")
            .replace(/\b\w/g, (l) => l.toUpperCase())
            .replace(/Cmu/g, "CMU")
            .replace(/Bms/g, "BMS")
            .replace(/Soc/g, "SOC")
            .replace(/Can/g, "CAN")
            .replace(/Ipm/g, "IPM")
            .replace(/Pwm/g, "PWM")
            .replace(/Dsp/g, "DSP")
            .replace(/Hw/g, "HW")
            .replace(/Uvlo/g, "UVLO");
    }

    // Computed values
    $: contactor_status = getFlagStatus($globalStore.metric.contactor_flags);
    $: bms_flag_status = getFlagStatus($globalStore.metric.bmsFlags);
    $: motor_limit_status = getFlagStatus($globalStore.metric.MotorLimits);
    $: motor_error_status = getFlagStatus($globalStore.metric.MotorErrors);
    $: motor_status = getFlagStatus({...$globalStore.metric.MotorLimits, ...$globalStore.metric.MotorErrors});
    // $: m = getFlagStatus($globalStore.metric.MotorErrors);

    $: overallSystemStatus = (() => {
        const statuses = [
            contactor_status,
            bms_flag_status,
            motor_limit_status,
            motor_error_status,
            ...$globalStore.metric.mppts.map((mppt) => getFlagStatus(mppt.flags)),
        ];

        if (statuses.includes("error")) return "error";
        if (statuses.includes("warning")) return "warning";
        return "ok";
    })();

    $: totalActiveAlerts = (() => {
        return [
            ...Object.values($globalStore.metric.contactor_flags),
            ...Object.values($globalStore.metric.bmsFlags),
            ...Object.values($globalStore.metric.MotorLimits),
            ...Object.values($globalStore.metric.MotorErrors),
            ...$globalStore.metric.mppts.flatMap((mppt) => Object.values(mppt.flags)),
        ].filter(Boolean).length;
    })();
</script>

<div class="dashboard-container">
    <!-- Header Stats -->
    <!-- <div class="stats-header">
        <div class="system-status-card {overallSystemStatus === 'ok' ? 'status-ok' : overallSystemStatus === 'warning' ? 'status-warning' : 'status-error'}">
            <div class="status-indicator">
                <div class="status-dot {overallSystemStatus === 'ok' ? 'dot-ok' : overallSystemStatus === 'warning' ? 'dot-warning' : 'dot-error'}"></div>
                <span class="status-text">Solar Vehicle Telemetry</span>
            </div>
            <div class="status-counts">
                <div class="count-item">
                    <span class="count-value {getStatusColor(overallSystemStatus)}">{overallSystemStatus.toUpperCase()}</span>
                    <span class="count-label">SYSTEM</span>
                </div>
                <div class="count-item">
                    <span class="count-value text-red-400">{totalActiveAlerts}</span>
                    <span class="count-label">ALERTS</span>
                </div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value text-blue-400">{formatValue(cabinSensors.Cabin_Temperature, "°C")}</div>
            <div class="stat-label">Cabin Temp</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value text-green-400">{formatValue(cabinSensors.Cabin_O2_Content, "%")}</div>
            <div class="stat-label">Oxygen Level</div>
        </div>
    </div> -->

    <!-- Sensor Grid -->
    <div class="sensor-grid">
        <!-- Cabin Air Quality -->
        <div class="category-panel bg-cyan-500/10 border-cyan-500/30">
            <div class="category-header">
                <span class="category-icon">🌬️</span>
                <span class="category-title text-cyan-400"
                    >CABIN AIR QUALITY</span
                >
            </div>

            <div class="sensors-compact-grid">
                {#each Object.entries($globalStore.metric.CabinSensors) as [key, value]}
                    {@const gasStatus = key.includes("_Content")
                        ? getGasLevelStatus(value, key)
                        : "ok"}
                    <div class="compact-sensor-card {getStatusBg(gasStatus)}">
                        <div class="sensor-label">
                            {key.replace("Cabin_", "").replace("_", " ")}
                        </div>
                        <div class="sensor-value {getStatusColor(gasStatus)}">
                            {formatValue(
                                value,
                                key.includes("Temperature")
                                    ? "°C"
                                    : key.includes("Pressure")
                                      ? "kPa"
                                      : key.includes("O2")
                                        ? "%"
                                        : "ppm"
                            )}
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Battery Contactors -->
        <div class="category-panel bg-yellow-500/5 border-yellow-500/20">
            <div class="category-header">
                <span class="category-icon">🔌</span>
                <span class="category-title text-yellow-400"
                    >BATTERY CONTACTORS</span
                >
                <div class="status-pill {contactor_status}">
                    {contactor_status.toUpperCase()}
                </div>
            </div>

            <div class="modern-flags-container">
                {#each Object.entries($globalStore.metric.contactor_flags) as [key, value]}
                    <div class="flag-indicator-row">
                        <div
                            class="flag-status-light {value
                                ? 'active'
                                : 'inactive'}"
                        >
                            <div class="status-ring"></div>
                            <div class="status-core"></div>
                        </div>
                        <div class="flag-info">
                            <div class="flag-name">{formatFlagName(key)}</div>
                            <div
                                class="flag-status-text {value
                                    ? 'text-red-300'
                                    : 'text-green-400'}"
                            >
                                {value ? "ACTIVE" : "NORMAL"}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- BMS Status -->
        <div class="category-panel bg-green-500/5 border-green-500/20">
            <div class="category-header">
                <span class="category-icon">🔋</span>
                <span class="category-title text-green-400"
                    >BATTERY MANAGEMENT</span
                >
                <div class="status-pill {bms_flag_status}">
                    {bms_flag_status.toUpperCase()}
                </div>
            </div>

            <div class="modern-flags-container">
                {#each Object.entries($globalStore.metric.bmsFlags) as [key, value]}
                    <div class="flag-indicator-row">
                        <div
                            class="flag-status-light {value
                                ? 'active'
                                : 'inactive'}"
                        >
                            <div class="status-ring"></div>
                            <div class="status-core"></div>
                        </div>
                        <div class="flag-info">
                            <div class="flag-name">{formatFlagName(key)}</div>
                            <div
                                class="flag-status-text {value
                                    ? 'text-red-300'
                                    : 'text-green-400'}"
                            >
                                {value ? "FAULT" : "OK"}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- CMU Temperatures -->
        <div class="category-panel bg-emerald-500/5 border-emerald-500/20">
            <div class="category-header">
                <span class="category-icon">🌡️</span>
                <span class="category-title text-emerald-400"
                    >CMU TEMPERATURES</span
                >
            </div>

            <div class="sensors-compact-grid">
                {#each $globalStore.metric.cmus as cmu, index}
                    <div
                        class="compact-sensor-card bg-gray-800/50 border-gray-700/50 backdrop-blur-sm"
                    >
                        <div class="sensor-label">{`CMU${index+1} Temp`}</div>
                        <div class="sensor-value text-emerald-300">
                            {formatValue(cmu.temperature, "°C")}
                        </div>
                    </div>
                    <div
                        class="compact-sensor-card bg-gray-800/50 border-gray-700/50 backdrop-blur-sm"
                    >
                        <div class="sensor-label">{`Cell${index+1} Temp`}</div>
                        <div class="sensor-value text-emerald-300">
                            {formatValue(cmu.cell_temperature, "°C")}
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Combined Motor System & Errors Panel -->
        <div
            class="category-panel bg-blue-500/5 border-blue-500/20 lg:col-span-2"
        >
            <div class="category-header">
                <span class="category-icon">⚡</span>
                <span class="category-title text-blue-400"
                    >MOTOR SYSTEM & ERRORS</span
                >
                <div
                    class="status-pill {motor_status}"
                >
                    {motor_status.toUpperCase()}
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <!-- Temperatures -->
                <div>
                    <h4 class="section-subtitle">Temperatures</h4>
                    <div class="sensors-compact-grid">
                        {#each MotorTempKeys as key, index}
                            <div
                                class="compact-sensor-card bg-gray-800/50 border-gray-700/50 backdrop-blur-sm"
                            >
                                <div class="sensor-label">
                                    {key.replace("_", " ")}
                                </div>
                                <div class="sensor-value text-blue-300">
                                    {formatValue($globalStore.metric[key] as any, "°C")}
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>

                <!-- System Limits -->
                <div>
                    <h4 class="section-subtitle">System Limits</h4>
                    <div class="modern-flags-container">
                        {#each Object.entries($globalStore.metric.MotorLimits) as [key, value]}
                            <div class="flag-indicator-row">
                                <div
                                    class="flag-status-light {value
                                        ? 'active'
                                        : 'inactive'}"
                                >
                                    <div class="status-ring"></div>
                                    <div class="status-core"></div>
                                </div>
                                <div class="flag-info">
                                    <div class="flag-name">
                                        {formatFlagName(key)}
                                    </div>
                                    <div
                                        class="flag-status-text {value
                                            ? 'text-orange-300'
                                            : 'text-green-400'}"
                                    >
                                        {value ? "LIMITED" : "NORMAL"}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Errors Section -->
            <div>
                <h4 class="section-subtitle">Motor Errors</h4>
                <div class="modern-flags-container">
                    {#each Object.entries($globalStore.metric.MotorErrors) as [key, value]}
                        <div class="flag-indicator-row">
                            <div
                                class="flag-status-light {value
                                    ? 'active error'
                                    : 'inactive'}"
                            >
                                <div class="status-ring"></div>
                                <div class="status-core"></div>
                            </div>
                            <div class="flag-info">
                                <div class="flag-name">
                                    {formatFlagName(key)}
                                </div>
                                <div
                                    class="flag-status-text {value
                                        ? 'text-red-300'
                                        : 'text-green-400'}"
                                >
                                    {value ? "ERROR" : "OK"}
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>

        <!-- Update the MPPT Controllers panel to span full width -->
        <!-- MPPT Controllers -->
        <div
            class="category-panel bg-orange-500/5 border-orange-500/20 lg:col-span-2"
        >
            <div class="category-header">
                <span class="category-icon">☀️</span>
                <span class="category-title text-orange-400"
                    >SOLAR MPPT CONTROLLERS</span
                >
            </div>

            <div class="mppt-grid">
                {#each $globalStore.metric.mppts as mppt, mpptIndex}
                    {@const mpptStatus = getFlagStatus(mppt.flags)}
                    <div
                        class="mppt-card {getStatusBg(
                            mpptStatus
                        )} backdrop-blur-sm"
                    >
                        <div class="mppt-header">
                            <span class="mppt-name">{mpptNames[mpptIndex]}</span>
                            <div class="status-pill {mpptStatus}">
                                {mpptStatus.toUpperCase()}
                            </div>
                        </div>

                        <div class="temp-readings">
                            <div class="temp-item">
                                <span class="temp-label">MOSFET</span>
                                <span class="temp-value"
                                    >{formatValue(
                                        mppt.Mosfet_Temperature,
                                        "°C"
                                    )}</span
                                >
                            </div>
                            <div class="temp-item">
                                <span class="temp-label">MPPT</span>
                                <span class="temp-value"
                                    >{formatValue(
                                        mppt.MPPT_Temperature,
                                        "°C"
                                    )}</span
                                >
                            </div>
                        </div>

                        <div class="mppt-flags">
                            <div class="flags-header">System Status</div>
                            <div class="modern-flags-compact">
                                {#each Object.entries(mppt.flags) as [key, value]}
                                    <div class="compact-flag-row">
                                        <div
                                            class="flag-status-dot {value
                                                ? 'active'
                                                : 'inactive'}"
                                        ></div>
                                        <div class="compact-flag-name">
                                            {formatFlagName(key)}
                                        </div>
                                        <div
                                            class="compact-flag-status {value
                                                ? 'text-red-300'
                                                : 'text-green-400'}"
                                        >
                                            {value ? "⚠" : "✓"}
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>

<style lang="postcss">
    @reference "tailwindcss";

    .dashboard-container {
        @apply p-4 space-y-6 bg-gray-900 min-h-screen;
        background: radial-gradient(
                circle at 20% 50%,
                rgba(59, 130, 246, 0.05) 0%,
                transparent 50%
            ),
            radial-gradient(
                circle at 80% 20%,
                rgba(16, 185, 129, 0.05) 0%,
                transparent 50%
            ),
            radial-gradient(
                circle at 40% 80%,
                rgba(245, 158, 11, 0.05) 0%,
                transparent 50%
            ),
            #0f172a;
    }

    .stats-header {
        @apply grid grid-cols-1 md:grid-cols-3 gap-4;
    }

    .system-status-card {
        @apply rounded-2xl p-6 border-2 transition-all duration-300 backdrop-blur-sm;
        background: rgba(15, 23, 42, 0.8);
    }

    .system-status-card.status-ok {
        @apply border-green-500/50 bg-green-500/5;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.1);
    }

    .system-status-card.status-warning {
        @apply border-orange-500/50 bg-orange-500/5;
        box-shadow: 0 0 20px rgba(249, 115, 22, 0.1);
    }

    .system-status-card.status-error {
        @apply border-red-500/50 bg-red-500/5;
        animation: critical-pulse 2s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
    }

    .status-indicator {
        @apply flex items-center gap-3 mb-4;
    }

    .status-dot {
        @apply w-4 h-4 rounded-full;
    }

    .status-dot.dot-ok {
        @apply bg-green-500;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-dot.dot-warning {
        @apply bg-orange-500;
        box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-dot.dot-error {
        @apply bg-red-500;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
        animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-text {
        @apply text-white font-bold text-base;
    }

    .status-counts {
        @apply flex justify-between;
    }

    .count-item {
        @apply text-center;
    }

    .count-value {
        @apply text-2xl font-bold block;
    }

    .count-label {
        @apply text-xs text-gray-400 font-medium;
    }

    .stat-card {
        @apply bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 text-center border border-gray-700/50;
    }

    .stat-value {
        @apply text-3xl font-bold;
    }

    .stat-label {
        @apply text-sm text-gray-400 mt-2 font-medium;
    }

    .sensor-grid {
        @apply grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6;
    }

    .category-panel {
        @apply rounded-2xl p-6 border backdrop-blur-sm transition-all duration-300;
        background: rgba(15, 23, 42, 0.6);
    }

    .category-header {
        @apply flex items-center justify-between mb-6;
    }

    .category-icon {
        @apply text-2xl;
    }

    .category-title {
        @apply font-bold text-sm flex-1 ml-3 tracking-wide;
    }

    .status-pill {
        @apply px-3 py-1 rounded-full text-xs font-bold;
    }

    .status-pill.ok {
        @apply bg-green-500/20 text-green-300 border border-green-500/30;
    }

    .status-pill.warning {
        @apply bg-orange-500/20 text-orange-300 border border-orange-500/30;
    }

    .status-pill.error {
        @apply bg-red-500/20 text-red-300 border border-red-500/30;
        animation: pill-pulse 2s ease-in-out infinite;
    }

    .sensors-compact-grid {
        @apply grid grid-cols-2 gap-3;
    }

    .compact-sensor-card {
        @apply rounded-xl p-4 border transition-all duration-300;
    }

    .sensor-label {
        @apply text-xs text-gray-400 font-medium mb-2;
    }

    .sensor-value {
        @apply text-lg font-bold;
    }

    /* Modern Flag Design */
    .modern-flags-container {
        @apply grid grid-cols-2 gap-3;
    }

    .flag-indicator-row {
        @apply flex items-center gap-4 p-3 rounded-xl bg-gray-800/30 border border-gray-700/30 transition-all duration-300 h-full;
    }

    .flag-indicator-row:hover {
        @apply bg-gray-800/50;
    }

    .flag-status-light {
        @apply relative w-6 h-6 flex-shrink-0 flex items-center justify-center;
    }

    .status-ring {
        @apply absolute inset-0 rounded-full border-2 opacity-60;
        border-color: currentColor;
    }

    .status-core {
        @apply w-3 h-3 rounded-full transition-all duration-300;
    }

    .flag-status-light .status-core {
        @apply scale-0;
    }

    .flag-status-light.active .status-core {
        @apply scale-100 bg-red-500;
    }

    .flag-status-light.inactive .status-core {
        @apply scale-100 bg-green-500;
    }

    .flag-status-light.active .status-ring {
        animation: ring-pulse 2s infinite;
    }

    .flag-info {
        @apply flex-1;
    }

    .flag-name {
        @apply text-sm font-medium;
    }

    .flag-status-text {
        @apply text-xs font-bold mt-1;
    }

    /* Motor System */
    .motor-section {
        @apply space-y-6;
    }

    .section-subtitle {
        @apply text-sm font-bold text-gray-300 mb-3;
    }

    /* MPPT Cards */
    .mppt-grid {
        @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
    }

    .mppt-card {
        @apply rounded-2xl p-4 border transition-all duration-300;
    }

    .mppt-header {
        @apply flex justify-between items-center mb-4;
    }

    .mppt-name {
        @apply font-bold text-gray-200;
    }

    .temp-readings {
        @apply grid grid-cols-2 gap-3 mb-4;
    }

    .temp-item {
        @apply bg-gray-800/30 p-3 rounded-lg;
    }

    .temp-label {
        @apply text-xs text-gray-400;
    }

    .temp-value {
        @apply font-bold text-lg;
    }

    .mppt-flags {
        @apply mt-4;
    }

    .flags-header {
        @apply text-xs text-gray-400 mb-2;
    }

    .modern-flags-compact {
        @apply grid grid-cols-2 gap-2;
    }

    .compact-flag-row {
        @apply flex items-center gap-2;
    }

    .flag-status-dot {
        @apply w-2 h-2 rounded-full;
    }

    .flag-status-dot.active {
        @apply bg-red-500;
    }

    .flag-status-dot.inactive {
        @apply bg-green-500;
    }

    .compact-flag-name {
        @apply text-xs text-gray-300 flex-1;
    }

    /* Animations */
    @keyframes pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    @keyframes critical-pulse {
        0%,
        100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
        }
    }

    @keyframes pill-pulse {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }

    @keyframes ring-pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        70% {
            box-shadow: 0 0 0 6px rgba(239, 68, 68, 0);
        }
    }
</style>
