<script>
    import { onMount, onDestroy } from "svelte";
    import Chart from "chart.js/auto";

    let canvas;
    let chart;
    const { leads } = $props();

    onMount(() => {
        const totals = leads.reduce(
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

        const totalLeads = leads.length || 1; // avoid divide by 0

        // 🔥 Conversion % per stage
        const conversionPercentages = [
            ((totals.NEW / totalLeads) * 100).toFixed(1),
            ((totals.IN_PROGRESS / totalLeads) * 100).toFixed(1),
            ((totals.WON / totalLeads) * 100).toFixed(1),
            ((totals.LOST / totalLeads) * 100).toFixed(1),
        ];

        chart = new Chart(canvas, {
            type: "bar",
            data: {
                labels: ["New", "In Progress", "Won", "Lost"],
                datasets: [
                    {
                        label: "Conversion %",
                        data: conversionPercentages,
                        borderWidth: 1,
                        barThickness: 18,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",
                layout: {
                    padding: 0,
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => `${value}%`,
                        },
                    },
                },
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.raw}% of total leads`,
                        },
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
    <h3>Pipeline Conversion by Stage</h3>
    <div class="chart-container">
        <canvas bind:this={canvas}></canvas>
    </div>
</div>

<style>
    .chart-card {
        width: 420px;
        height: 320px;
        padding: 1rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
    }

    .chart-container {
        flex: 1;
        position: relative;
    }

    canvas {
        width: 100% !important;
        height: 100% !important;
    }
</style>
