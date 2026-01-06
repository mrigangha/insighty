<script>
    import { onMount, onDestroy } from "svelte";
    import Chart from "chart.js/auto";

    let canvas;
    let chart;
    const { leads } = $props();

    onMount(() => {
        const statusCounts = leads.reduce(
            (acc, lead) => {
                acc[lead.status] = (acc[lead.status] || 0) + 1;
                return acc;
            },
            {
                NEW: 0,
                IN_PROGRESS: 0,
                WON: 0,
                LOST: 0,
            },
        );

        chart = new Chart(canvas, {
            type: "bar",
            data: {
                labels: ["New", "In Progress", "Won", "Lost"],
                datasets: [
                    {
                        label: "Leads",
                        data: [
                            statusCounts.NEW,
                            statusCounts.IN_PROGRESS,
                            statusCounts.WON,
                            statusCounts.LOST,
                        ],
                        borderWidth: 1,
                        barThickness: 18, // 🔥 keeps bars compact
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",
                layout: {
                    padding: 0, // 🔥 remove extra spacing
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                        },
                    },
                },
                plugins: {
                    legend: {
                        position: "bottom", // 🔥 same as pie
                    },
                },
            },
        });
    });

    onDestroy(() => {
        chart?.destroy();
    });
</script>

<div class="chart-card">
    <h3>Leads by Status</h3>
    <div class="chart-container">
        <canvas bind:this={canvas}></canvas>
    </div>
</div>

<style>
    .chart-card {
        width: 420px;
        height: 320px; /* 🔥 FIX: same card height as pie */
        padding: 1rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
    }

    .chart-container {
        flex: 1; /* 🔥 forces canvas to fill remaining space */
        position: relative;
    }

    canvas {
        width: 100% !important;
        height: 100% !important;
    }
</style>
