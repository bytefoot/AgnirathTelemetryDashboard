<!-- NotificationToast.svelte -->
<script lang="ts">
    import { globalStore, type BMSNotification } from '$lib/store';
    import { onMount } from 'svelte';
    
    let notifications: BMSNotification[] = $state([]);
    
    // Subscribe to notifications
    onMount(() => {
        const unsubscribe = globalStore.notifications.subscribe((value) => {
            notifications = value;
        });
        
        return unsubscribe;
    });
    
    // Auto-remove notifications after 10 seconds
    function autoRemoveNotification(notification: BMSNotification) {
        setTimeout(() => {
            globalStore.removeNotification(notification.id);
        }, 10000);
    }
    
    // Format timestamp for display
    function formatTime(date: Date): string {
        return date.toLocaleTimeString();
    }
    
    // Get icon based on severity
    function getIcon(severity: string): string {
        switch (severity) {
            case 'error': return '🚨';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '🔔';
        }
    }
    
    // Auto-remove notifications when they appear
    $effect(() => {
        notifications.forEach(notification => {
            autoRemoveNotification(notification);
        });
    });
</script>

<!-- Notification Container -->
<div class="fixed top-4 right-4 z-50 max-w-sm space-y-2">
    {#each notifications as notification (notification.id)}
        <div 
            class="bg-gray-800 border-l-4 rounded-lg shadow-lg p-4 animate-slide-in
                   {notification.severity === 'error' ? 'border-red-500' : ''}
                   {notification.severity === 'warning' ? 'border-yellow-500' : ''}
                   {notification.severity === 'info' ? 'border-blue-500' : ''}"
        >
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <span class="text-xl">{getIcon(notification.severity)}</span>
                    <div>
                        <div class="text-white font-medium text-sm">
                            {notification.message}
                        </div>
                        <div class="text-gray-400 text-xs mt-1">
                            {formatTime(notification.timestamp)}
                        </div>
                    </div>
                </div>
                <button
                    onclick={() => globalStore.removeNotification(notification.id)}
                    class="text-gray-400 hover:text-white ml-4 p-1"
                    title="Dismiss"
                >
                    ✕
                </button>
            </div>
        </div>
    {/each}
</div>

<!-- Notification Summary (when there are many) -->
{#if notifications.length > 3}
    <div class="fixed top-4 right-4 z-40 max-w-sm">
        <div class="bg-gray-700 rounded-lg p-3 text-white text-sm">
            <div class="flex items-center justify-between">
                <span>{notifications.length} active alerts</span>
                <button
                    onclick={() => globalStore.clearNotifications()}
                    class="text-gray-300 hover:text-white text-xs px-2 py-1 bg-gray-600 rounded"
                >
                    Clear All
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
</style>