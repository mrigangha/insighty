<script>
    import { onMount, onDestroy } from "svelte";
    import Chart from "chart.js/auto";

    const { leads } = $props();

    let canvas;
    let myPieChart;

    // ─────────────────────────────
    // Conversion logic
    // ─────────────────────────────
    const totalLeads = leads.length;
    const convertedLeads = leads.filter((lead) => lead.status === "WON").length;

    const conversionRate =
        totalLeads > 0 ? ((convertedLeads / totalLeads) * 100).toFixed(1) : 0;

    // ─────────────────────────────
    // Source aggregation (example)
    // ─────────────────────────────
    function groupBySource(leads) {
        const map = {};
        leads.forEach((lead) => {
            const source = lead.source || "Unknown";
            map[source] = (map[source] || 0) + 1;
        });
        return map;
    }

    onMount(() => {
        const ctx = canvas.getContext("2d");

        const sourceMap = groupBySource(leads);

        myPieChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: Object.keys(sourceMap),
                datasets: [
                    {
                        data: Object.values(sourceMap),
                        backgroundColor: [
                            "#4f46e5",
                            "#22c55e",
                            "#f59e0b",
                            "#ef4444",
                            "#06b6d4",
                        ],
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                },
            },
        });
    });

    onDestroy(() => {
        myPieChart?.destroy();
    });
</script>

<div class="chart-card">
    <h3>Leads by Source</h3>

    <!-- 🔥 Conversion Insight -->
    <div class="conversion">
        <strong>{conversionRate}%</strong>
        <span>conversion rate</span>
    </div>

    <div class="chart-container">
        <canvas bind:this={canvas}></canvas>
    </div>
</div>

<style>
    .chart-card {
        width: 420px;
        padding: 1rem;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }

    .conversion {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        color: #16a34a;
    }

    .conversion strong {
        font-size: 1.6rem;
        font-weight: 700;
    }

    .conversion span {
        font-size: 0.9rem;
        color: #555;
    }

    .chart-container {
        height: 240px;
    }
</style>
