<script>
    import { onMount } from "svelte";
    import { push } from "svelte-spa-router";
    import {
        getLoggedIn,
        getOpenProjectId,
        URL,
        getAccessToken,
    } from "../lib/store.svelte";
    import { Chart } from "chart.js/auto";
    import { get } from "svelte/store";

    let projectId = $derived(getOpenProjectId());
    let events = $state([]);
    let clickEvents = $state([]);

    let viewsCanvas;
    let funnelCanvas;

    let viewsChart;
    let funnelChart;

    let viewsTitle = $state("Page Views");
    let funnelTitle = $state("Funnel");

    let editViews = $state(false);
    let editFunnel = $state(false);

    let funnelSteps = $state(["/"]); // default funnel step
    let stageInsights = $state([]); // page views, clicks, conversion per step

    onMount(async () => {
        viewsTitle =
            localStorage.getItem(`viewsTitle:${projectId}`) || "Page Views";
        funnelTitle =
            localStorage.getItem(`funnelTitle:${projectId}`) || "Funnel";

        if (!getLoggedIn()) push("/login");
        const token = getAccessToken();
        if (!token) push("/profile");

        // fetch page views
        const res = await fetch(`${URL}/page-views/${projectId}/`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return alert("Unable to fetch analytics");
        events = await res.json().then((d) => d.views);

        // fetch clicks
        const resp = await fetch(`${URL}/click/${projectId}/`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) return alert("Unable to fetch click analytics");
        clickEvents = await resp.json().then((d) => d.clicks);

        computeStageInsights();
        renderViewsChart();
        renderFunnelChart();
    });

    function saveTitle(type) {
        if (type === "views") {
            localStorage.setItem(`viewsTitle:${projectId}`, viewsTitle);
            editViews = false;
        }
        if (type === "funnel") {
            localStorage.setItem(`funnelTitle:${projectId}`, funnelTitle);
            editFunnel = false;
        }
    }

    function addStep() {
        funnelSteps.push("");
        computeStageInsights();
        renderFunnelChart();
    }

    function removeStep(index) {
        funnelSteps.splice(index, 1);
        computeStageInsights();
        renderFunnelChart();
    }

    function computeStageInsights() {
        // compute views, clicks, and conversion rate
        stageInsights = funnelSteps.map((step, i) => {
            const views = events.find((e) => e.path === step)?.count ?? 0;
            const clicks = clickEvents
                .filter((c) => c.path === step)
                .reduce((a, b) => a + b.count, 0);

            let conversion =
                i > 0
                    ? (
                          (views /
                              (events.find((e) => e.path === funnelSteps[i - 1])
                                  ?.count || 1)) *
                          100
                      ).toFixed(1)
                    : null;

            return { step, views, clicks, conversion };
        });
    }

    function renderViewsChart() {
        viewsChart?.destroy();
        viewsChart = new Chart(viewsCanvas, {
            type: "bar",
            data: {
                labels: events.map((e) => e.path),
                datasets: [
                    {
                        label: "Page Views",
                        data: events.map((e) => e.count),
                        borderRadius: 8,
                        backgroundColor: "#6366f1",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true } },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } },
                    x: { grid: { display: false } },
                },
            },
        });
    }

    function renderFunnelChart() {
        if (!funnelCanvas) return;
        funnelChart?.destroy();

        const viewsData = stageInsights.map((s) => s.views);
        const clicksData = stageInsights.map((s) => s.clicks);

        funnelChart = new Chart(funnelCanvas, {
            type: "bar",
            data: {
                labels: stageInsights.map((s) => s.step),
                datasets: [
                    {
                        label: "Page Views",
                        data: viewsData,
                        backgroundColor: "#6366f1",
                        borderRadius: 8,
                    },
                    {
                        label: "Clicks",
                        data: clicksData,
                        backgroundColor: "#10b981",
                        borderRadius: 8,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const stage = stageInsights[ctx.dataIndex];
                                let extra =
                                    ctx.dataset.label === "Page Views" &&
                                    stage.conversion
                                        ? ` | Conversion: ${stage.conversion}%`
                                        : "";
                                return `${ctx.dataset.label}: ${ctx.raw} users${extra}`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { display: false },
                    },
                    y: { grid: { display: false } },
                },
            },
        });
    }
</script>

<div class="dashboard-container">
    <!-- Page Header -->
    <div class="page-header">
        <div>
            <h1 class="page-title">Analytics Dashboard</h1>
            <p class="page-subtitle">
                Track your project performance and user behavior
            </p>
        </div>
    </div>

    <!-- Main Charts Grid -->
    <div class="analytics-grid">
        <div class="card chart-card">
            <div class="card-header">
                {#if editViews}
                    <div class="edit-group">
                        <input
                            type="text"
                            bind:value={viewsTitle}
                            class="title-input"
                            autofocus
                        />
                        <button
                            class="btn-save"
                            on:click={() => saveTitle("views")}
                        >
                            ✓
                        </button>
                    </div>
                {:else}
                    <div class="card-title-group">
                        <h3 on:click={() => (editViews = true)}>
                            {viewsTitle}
                            <span class="edit-icon">✎</span>
                        </h3>
                        <div class="metric-badge">
                            {events.reduce((a, b) => a + b.count, 0)} total views
                        </div>
                    </div>
                {/if}
            </div>
            <div class="chart-container">
                <canvas bind:this={viewsCanvas}></canvas>
            </div>
        </div>

        <div class="card chart-card">
            <div class="card-header">
                {#if editFunnel}
                    <div class="edit-group">
                        <input
                            type="text"
                            bind:value={funnelTitle}
                            class="title-input"
                            autofocus
                        />
                        <button
                            class="btn-save"
                            on:click={() => saveTitle("funnel")}
                        >
                            ✓
                        </button>
                    </div>
                {:else}
                    <div class="card-title-group">
                        <h3 on:click={() => (editFunnel = true)}>
                            {funnelTitle}
                            <span class="edit-icon">✎</span>
                        </h3>
                        <div class="metric-badge">
                            {funnelSteps.length} steps configured
                        </div>
                    </div>
                {/if}
            </div>
            <div class="chart-container">
                <canvas bind:this={funnelCanvas}></canvas>
            </div>
        </div>
    </div>

    <!-- Funnel Configuration & Insights -->
    <div class="layout-grid">
        <div class="card panel-card">
            <div class="panel-header">
                <div>
                    <h4>Funnel Configuration</h4>
                    <p class="panel-description">
                        Define your conversion funnel steps
                    </p>
                </div>
                <button class="btn-add" on:click={addStep}>
                    <span class="btn-icon">+</span> Add Step
                </button>
            </div>
            <div class="funnel-list">
                {#each funnelSteps as step, i}
                    <div class="funnel-step-row">
                        <div class="step-number">{i + 1}</div>
                        <input
                            type="text"
                            bind:value={funnelSteps[i]}
                            on:input={() => {
                                computeStageInsights();
                                renderFunnelChart();
                            }}
                            placeholder="/path/to/page"
                            class="font-mono step-input"
                        />
                        {#if funnelSteps.length > 1}
                            <button
                                class="btn-remove"
                                on:click={() => removeStep(i)}
                                title="Remove step"
                            >
                                ×
                            </button>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>

        <div class="card panel-card">
            <div class="panel-header">
                <div>
                    <h4>Conversion Breakdown</h4>
                    <p class="panel-description">
                        Step-by-step funnel performance
                    </p>
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Funnel Step</th>
                            <th class="text-right">Views</th>
                            <th class="text-right">Drop-off Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each stageInsights as s, i}
                            <tr>
                                <td>
                                    <div class="step-cell">
                                        <span class="step-badge">{i + 1}</span>
                                        <span class="font-mono"
                                            >{s.step || "(empty)"}</span
                                        >
                                    </div>
                                </td>
                                <td class="text-right font-semibold"
                                    >{s.views}</td
                                >
                                <td class="text-right">
                                    {#if s.conversion}
                                        <span class="badge badge-success"
                                            >{s.conversion}%</span
                                        >
                                    {:else}
                                        <span class="text-muted">—</span>
                                    {/if}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Interaction Events -->
    <div class="card">
        <div class="panel-header">
            <div>
                <h4>Interaction Events</h4>
                <p class="panel-description">
                    User click tracking across your application
                </p>
            </div>
        </div>
        <div class="table-wrapper">
            {#if clickEvents.length}
                <table>
                    <thead>
                        <tr>
                            <th>Page Path</th>
                            <th>Target Element</th>
                            <th class="text-right">Click Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each clickEvents as c}
                            <tr>
                                <td class="font-mono path-cell">{c.path}</td>
                                <td>
                                    <span class="element-tag">{c.target}</span>
                                </td>
                                <td class="text-right">
                                    <span class="count-badge">{c.count}</span>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <p class="empty-title">No interaction events yet</p>
                    <p class="empty-description">
                        Click events will appear here once users interact with
                        your application
                    </p>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #10b981;
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --border: #e2e8f0;
        --accent-hover: #eef2ff;
        --success-bg: #ecfdf5;
        --success-text: #059669;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    * {
        box-sizing: border-box;
    }

    /* Base Layout */
    .dashboard-container {
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter",
            sans-serif;
        background: var(--bg);
        padding: 40px;
        color: var(--text-main);
        min-height: 100vh;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* Page Header */
    .page-header {
        margin-bottom: 40px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border);
    }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        color: var(--text-main);
        letter-spacing: -0.02em;
    }

    .page-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* Grids */
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        gap: 28px;
        margin-bottom: 28px;
    }

    .layout-grid {
        display: grid;
        grid-template-columns: 1fr 1.5fr;
        gap: 28px;
        margin-bottom: 28px;
    }

    /* Cards */
    .card {
        background: var(--card-bg);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 28px;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
    }

    .chart-card {
        padding: 32px;
    }

    .panel-card {
        display: flex;
        flex-direction: column;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
        min-height: 48px;
    }

    .card-title-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
    }

    .card-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        color: var(--text-main);
        transition: color 0.2s;
    }

    .card-header h3:hover {
        color: var(--primary);
    }

    .edit-icon {
        font-size: 0.9rem;
        color: var(--text-muted);
        opacity: 0;
        transition: opacity 0.2s;
    }

    .card-header h3:hover .edit-icon {
        opacity: 1;
    }

    .metric-badge {
        display: inline-flex;
        align-items: center;
        font-size: 0.875rem;
        color: var(--text-secondary);
        background: var(--bg);
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 500;
        width: fit-content;
    }

    .chart-container {
        position: relative;
        height: 320px;
        width: 100%;
    }

    /* Inputs & Forms */
    .edit-group {
        display: flex;
        gap: 10px;
        width: 100%;
    }

    .title-input {
        flex: 1;
        font-size: 1.25rem;
        font-weight: 600;
        padding: 8px 12px;
        border: 2px solid var(--primary);
        border-radius: 10px;
        outline: none;
        color: var(--text-main);
    }

    input[type="text"] {
        width: 100%;
        padding: 12px 16px;
        border: 1px solid var(--border);
        border-radius: 10px;
        outline: none;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        background: var(--card-bg);
    }

    input[type="text"]:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    }

    .step-input {
        flex: 1;
    }

    /* Buttons */
    button {
        cursor: pointer;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
        font-family: inherit;
    }

    .btn-save {
        background: var(--primary);
        color: white;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 1.125rem;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 44px;
    }

    .btn-save:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    .btn-add {
        background: var(--primary);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 0.9375rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: var(--shadow-sm);
    }

    .btn-add:hover {
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .btn-icon {
        font-size: 1.25rem;
        line-height: 1;
    }

    .btn-remove {
        background: transparent;
        color: var(--text-muted);
        width: 36px;
        height: 36px;
        border-radius: 8px;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .btn-remove:hover {
        background: #fee2e2;
        color: #ef4444;
    }

    /* Panel Header */
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
        gap: 16px;
    }

    .panel-header h4 {
        margin: 0 0 4px 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-main);
    }

    .panel-description {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    /* Funnel Editor */
    .funnel-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .funnel-step-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .step-number {
        background: var(--primary);
        color: white;
        width: 32px;
        height: 32px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-size: 0.875rem;
        font-weight: 700;
        box-shadow: var(--shadow-sm);
    }

    /* Tables */
    .table-wrapper {
        overflow-x: auto;
        width: 100%;
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9375rem;
    }

    th {
        text-align: left;
        font-size: 0.8125rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        padding: 16px 20px;
        background: var(--bg);
        font-weight: 600;
        border-bottom: 1px solid var(--border);
    }

    td {
        padding: 16px 20px;
        border-bottom: 1px solid var(--border);
        color: var(--text-main);
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    tbody tr {
        transition: background-color 0.15s ease;
    }

    tbody tr:hover {
        background: #f8fafc;
    }

    .step-cell {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: var(--primary);
        color: white;
        border-radius: 50%;
        font-size: 0.75rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .path-cell {
        color: var(--primary);
        font-weight: 500;
    }

    .font-mono {
        font-family:
            ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.875rem;
    }

    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8125rem;
        display: inline-block;
    }

    .badge-success {
        background: var(--success-bg);
        color: var(--success-text);
    }

    .element-tag {
        background: var(--bg);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8125rem;
        color: var(--text-secondary);
        font-family: monospace;
        border: 1px solid var(--border);
        display: inline-block;
    }

    .count-badge {
        background: var(--primary);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    }

    .text-right {
        text-align: right;
    }

    .font-semibold {
        font-weight: 600;
    }

    .text-muted {
        color: var(--text-muted);
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        opacity: 0.5;
    }

    .empty-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-main);
        margin: 0 0 8px 0;
    }

    .empty-description {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        margin: 0;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Responsive */
    @media (max-width: 1200px) {
        .layout-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .dashboard-container {
            padding: 20px;
        }

        .page-header {
            margin-bottom: 28px;
            padding-bottom: 20px;
        }

        .page-title {
            font-size: 1.5rem;
        }

        .analytics-grid {
            grid-template-columns: 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .layout-grid {
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            padding: 20px;
        }

        .chart-card {
            padding: 24px;
        }

        .chart-container {
            height: 280px;
        }

        th,
        td {
            padding: 12px 16px;
        }
    }

    @media (max-width: 480px) {
        .dashboard-container {
            padding: 16px;
        }

        .page-title {
            font-size: 1.25rem;
        }

        .page-subtitle {
            font-size: 0.875rem;
        }

        .card {
            padding: 16px;
        }

        .chart-card {
            padding: 20px;
        }

        .panel-header {
            flex-direction: column;
            align-items: flex-start;
        }

        th,
        td {
            padding: 10px 12px;
            font-size: 0.875rem;
        }
    }
</style>
