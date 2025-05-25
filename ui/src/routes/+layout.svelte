<script>
    import "../app.css";
    import { onMount } from "svelte";

    let { children } = $props();
    let connected = false;
</script>

<svelte:head>
    <title>Solar Car Telemetry Dashboard</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-gray-200">
    <header class="bg-gray-800 border-b border-gray-700 p-4">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <img src="/logo.png" class="h-12" alt="Description" />
                <h1 class="text-2xl font-bold text-white">
                    Agnirath Telemetry Dashboard
                </h1>
                <div class="flex items-center space-x-2">
                    <div
                        class="w-3 h-3 rounded-full {connected
                            ? 'bg-green-500'
                            : 'bg-red-500'}"
                    ></div>
                    <span class="text-sm text-gray-300">
                        {connected ? "Connected" : "Disconnected"}
                    </span>
                </div>
            </div>
            <div class="text-sm text-gray-400">Live Telemetry Dashboard</div>
        </div>
    </header>

    {@render children()}
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
    }
</style>
