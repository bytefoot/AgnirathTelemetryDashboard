<script lang='ts'>
    import "../app.css";
    import { onMount, onDestroy } from "svelte";
    import { globalStore} from '$lib/store';
    import type {DataPacket, UpdatePacket} from "$lib/store_types.ts"

    let { children } = $props();

    // WebSocket connection
    let socket: WebSocket | null = null;
    let reconnectInterval: number | null = null;

    // Backend configuration
    const API_BASE_URL = 'http://localhost:8000';
    const WS_URL = 'ws://localhost:8000/ws/updates';
    let connected = $state(false);

    function connectWebSocket(): void {
        if (socket && socket.readyState === WebSocket.OPEN) return;
        
        // connectionStatus = 'connecting';
        socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            // connectionStatus = 'connected';
            connected = true;
            console.log('WebSocket connected');
            
            // Clear any reconnection attempts
            if (reconnectInterval) {
                clearInterval(reconnectInterval);
                reconnectInterval = null;
            }
        };

        socket.onmessage = (event) => {
            try {
                const data: UpdatePacket | DataPacket = JSON.parse(event.data);
                if(data.type == 'update'){
                    globalStore.handleWebSocketUpdate(data);
                }
                else if(data.type == 'data'){
                    globalStore.handleWebSocketData(data);
                }
                
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        socket.onclose = (event) => {
            // connectionStatus = 'disconnected';
            connected = false;
            console.log('WebSocket disconnected:', event.code, event.reason);
            
            // Attempt to reconnect after 3 seconds
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket();
                }, 3000);
            }
        };

        socket.onerror = (error) => {
            // connectionStatus = 'error';
            console.error('WebSocket error:', error);
        };
    }

    onMount(async () => {
        connectWebSocket();
    })

    onDestroy(() => {
        // Cleanup WebSocket
        if (socket) {
            socket.close();
        }
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
        }
    })

    const navItems = [
        { name: 'Overview', path: '/', icon: '🏠' },
        { name: 'Battery', path: '/battery', icon: '🔋' },
        { name: 'Motor', path: '/motor', icon: '⚙️' },
        { name: 'Solar', path: '/solar', icon: '☀️' },
        { name: 'Strategy', path: '/strategy', icon: '📋' },
        { name: 'Temperature', path: '/temperature', icon: '🌡️' }
    ];
    
    import { page } from '$app/stores'

    // Check if current route is active
    function isActive(path: string): boolean {
        if (path === '/') {
            return $page.url.pathname === '/';
        }
        return $page.url.pathname.startsWith(path);
    }

    // Fullscreen state
    let isFullscreen = $state(false);
    let layoutElement: HTMLElement;

    // Toggle fullscreen
    async function toggleFullscreen() {
        try {
            if (!document.fullscreenElement) {
                await document.documentElement.requestFullscreen();
                isFullscreen = true;
            } else {
                await document.exitFullscreen();
                isFullscreen = false;
            }
        } catch (error) {
            console.error('Error toggling fullscreen:', error);
        }
    }
    
    // Handle escape key
    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape' && document.fullscreenElement) {
            document.exitFullscreen();
            isFullscreen = false;
        }
    }
    
    // Handle fullscreen change events
    function handleFullscreenChange() {
        isFullscreen = !!document.fullscreenElement;
    }
    
    onMount(() => {
        document.addEventListener('keydown', handleKeydown);
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        
        return () => {
            document.removeEventListener('keydown', handleKeydown);
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
        };
    });
</script>

<svelte:head>
    <title>Agnirath</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-gray-200" bind:this={layoutElement}>
    <!-- Header - Hidden in fullscreen -->
    <header class="bg-gray-800 border-b border-gray-700 p-4 {isFullscreen ? 'hidden' : 'block'}">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <img src="/logo.png" class="h-12" alt="Agnirath Logo" />
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
            <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-400">Live Telemetry Dashboard</div>
                <!-- Fullscreen Toggle Button -->
                <button
                    onclick={toggleFullscreen}
                    class="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 text-sm"
                    title="Toggle Fullscreen (ESC to exit)"
                >
                    <span class="text-lg">{isFullscreen ? '🪟' : '⛶'}</span>
                    <span>{isFullscreen ? 'Exit' : 'Fullscreen'}</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Navigation Bar - Hidden in fullscreen -->
    <nav class="bg-gray-800 border-b border-gray-700 {isFullscreen ? 'hidden' : 'block'}">
        <div class="px-4">
            <div class="flex justify-between">
                {#each navItems as item}
                    <a
                        href={item.path}
                        class="relative flex items-center justify-center space-x-2 px-6 py-4 text-sm font-medium transition-colors duration-200 hover:bg-gray-700 flex-1 {isActive(item.path)
                            ? 'text-blue-400 bg-gray-700'
                            : 'text-gray-300 hover:text-white'}"
                    >
                        <span class="text-lg">{item.icon}</span>
                        <span>{item.name}</span>
                        
                        <!-- Active indicator -->
                        {#if isActive(item.path)}
                            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-400"></div>
                        {/if}
                    </a>
                {/each}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 {isFullscreen ? 'min-h-screen' : ''}">
        {#if isFullscreen}
            <!-- Fullscreen exit hint -->
            <div class="absolute top-4 right-4 z-50">
                <div class="bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg text-sm backdrop-blur-sm">
                    Press <kbd class="bg-gray-700 px-2 py-1 rounded text-xs">ESC</kbd> to exit fullscreen
                </div>
            </div>
        {/if}
        {@render children()}
    </main>
</div>
<style>
    :global(body) {
        margin: 0;
        padding: 0;
    }

    /* Custom scrollbar for webkit browsers */
    :global(::-webkit-scrollbar) {
        width: 6px;
        height: 6px;
    }
    
    :global(::-webkit-scrollbar-track) {
        background: #374151;
    }
    
    :global(::-webkit-scrollbar-thumb) {
        background: #6b7280;
        border-radius: 3px;
    }
    
    :global(::-webkit-scrollbar-thumb:hover) {
        background: #9ca3af;
    }
</style>
