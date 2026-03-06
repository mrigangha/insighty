<script>
    import Chart from "chart.js/auto";
    import "chartjs-adapter-date-fns";
    import { push } from "svelte-spa-router";

    import {
        URL,
        getLoggedIn,
        getOpenProjectId,
        getAccessToken,
    } from "../lib/store.svelte";
    import { onMount } from "svelte";

    /* ---------- props ---------- */
    let { SessionId, onback, leadId } = $props();

    /* ---------- state ---------- */
    let loading = $state(true);
    let graphCanvas = $state(null);
    let chart = $state(null);
    let clickRankingCanvas = $state(null);
    let clickRankingChart = $state(null);
    let path = [];
    let computeSucces = $state(0);
    let rScore = $state(0);
    let summary = $state({
        pages: 0,
        duration: 0,
        maxScroll: 0,
        clicks: 0,
    });
    let mostInteractedPages = $state([]);
    let keyInsight = $state("");
    const Utils = {
        CHART_COLORS: {
            red: "rgb(255, 99, 132)",
            blue: "rgb(54, 162, 235)",
            green: "rgb(75, 192, 192)",
            orange: "rgb(255, 159, 64)",
            purple: "rgb(153, 102, 255)",
            yellow: "rgb(255, 205, 86)",
        },
    };

    /* ---------- effect: fetch + render ---------- */
    onMount(async () => {
        if (!graphCanvas) return;

        if (!getLoggedIn()) {
            push("/login");
            return;
        }

        const token = getAccessToken();
        if (!token) {
            push("/profile");
            return;
        }

        const res = await fetch(
            `${URL}/events/${getOpenProjectId()}/${SessionId}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            },
        );

        if (!res.ok) {
            alert("Unable to fetch session events");
            return;
        }

        const data = await res.json();
        const events = data.session ?? [];
        if (events.length === 0) {
            loading = false;
            return;
        }
        const scrollGroups = groupScrollEventsByPath(events);
        const clickGroups = groupClickEventsByPath(events);
        let groupData = [];
        let group = {};
        let scrollEvents = [];
        scrollGroups.forEach((e) => {
            e.events.forEach((ev) => {
                scrollEvents.push(ev);
            });
        });
        let clicks = [];
        clickGroups.forEach((e) => {
            e.events.forEach((p) => {
                let key = e.path + ":" + p.text;
                clicks.push({ path: e.path, text: p.text });
                if (!(key in group)) {
                    group[key] = 1;
                } else {
                    group[key] += 1;
                }
            });
        });
        let grpLabels = [];
        let grpData = [];

        Object.keys(group).forEach((key) => {
            grpLabels.push(key);
            grpData.push(group[key]);
        });
        if (!scrollGroups.length && !clickGroups.length) return;

        const colors = Object.values(Utils.CHART_COLORS);

        /* ---------- click datasets ---------- */
        const clickDatasets = clickGroups.map((page, i) => ({
            label: `${page.path} (click)`,
            type: "scatter",
            showLine: false,
            data: page.events.map((e, idx) => ({
                x: e.time.getTime(),
                y: 105 + idx * 5, // separate multiple clicks vertically
                clickText: e.text, // tooltip text
            })),
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: colors[i % colors.length],
        }));

        /* ---------- scroll datasets ---------- */
        const scrollDatasets = scrollGroups.map((page, i) => ({
            label: page.path,
            type: "line",
            data: page.events.map((e) => ({
                x: e.time.getTime(),
                y: e.value,
            })),
            borderColor: colors[i % colors.length],
            tension: 0.35,
            fill: false,
        }));

        const datasets = [...scrollDatasets, ...clickDatasets];

        /* ---------- destroy old chart ---------- */
        if (chart) {
            chart.destroy();
            chart = null;
        }
        chart?.destroy();
        /* ---------- create chart ---------- */
        chart = new Chart(graphCanvas, {
            data: { datasets },
            options: {
                responsive: true,
                parsing: false,
                maintainAspectRatio: false, // Added to fit container
                interaction: {
                    mode: "nearest",
                    intersect: false,
                },
                scales: {
                    x: {
                        type: "time",
                        time: { unit: "second" },
                        title: {
                            display: true,
                            text: "Session Time",
                        },
                        grid: { display: false },
                    },
                    y: {
                        min: 0,
                        max: 130,
                        title: {
                            display: true,
                            text: "Scroll %",
                        },
                        ticks: {
                            callback: (v) => (v <= 100 ? `${v}%` : "Click"),
                        },
                        grid: { color: "#f3f4f6" },
                    },
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                if (ctx.raw.y > 100) {
                                    return ctx.raw.clickText || "Click event";
                                }
                                return `Scroll: ${ctx.raw.y}%`;
                            },
                        },
                    },
                },
            },
        });
        const pageInteractionMap = {};

        // scroll interactions
        scrollGroups.forEach((g) => {
            pageInteractionMap[g.path] ??= 0;
            pageInteractionMap[g.path] += g.events.length;
        });

        // click interactions
        clickGroups.forEach((g) => {
            pageInteractionMap[g.path] ??= 0;
            pageInteractionMap[g.path] += g.events.length * 2; // clicks weighted higher
        });

        mostInteractedPages = Object.entries(pageInteractionMap)
            .map(([path, score]) => ({ path, score }))
            .sort((a, b) => b.score - a.score)
            .slice(0, 5); // top 5
        renderFunnelChart(grpLabels, grpData);
        let score = scoreFromScroll(scrollEvents);
        const sessionDuration = getSessionDuration(events);
        score += scoreFromInteraction(grpLabels, sessionDuration);
        score += scoreFromRepetition(clicks);
        score += scoreFromNavigation(path);
        score += scoreFromCompletion();
        rScore = Math.max(0, Math.min(score, 100));
        let maxScroll = Math.max(...scrollEvents.map((e) => e.value), 0);
        let totalClicks = clicks.length;
        let uniquePages = new Set(path).size;

        summary = {
            pages: uniquePages,
            duration: sessionDuration,
            scroll: maxScroll,
            clicks: totalClicks,
        };
        function calculateKeyInsight() {
            if (computeSucces)
                return "Completed conversion flow (high buying intent)";

            if (summary.scroll >= 80 && summary.clicks >= 3)
                return "Highly engaged with content";

            if (summary.clicks >= 5)
                return "Repeated interaction suggests strong interest";

            if (summary.pages >= 3) return "Exploring multiple pages";

            return "Low engagement session";
        }
        keyInsight = calculateKeyInsight();

        loading = false;
    });
    $effect(() => {});

    /* Refined colors for better UI visuals */
    let intentBadge = $derived.by(() => {
        if (rScore >= 70)
            return { label: "High Intent", color: "#15803d", bg: "#dcfce7" }; // Green
        if (rScore >= 40)
            return { label: "Medium Intent", color: "#c2410c", bg: "#ffedd5" }; // Orange
        return { label: "Low Intent", color: "#b91c1c", bg: "#fee2e2" }; // Red
    });

    function scoreFromCompletion() {
        if (computeSucces !== 0) {
            return 40;
        }

        return 0;
    }
    function scoreFromNavigation(paths) {
        const uniquePages = new Set(paths).size;

        if (uniquePages >= 5) return 25;
        if (uniquePages >= 3) return 15;
        if (uniquePages >= 2) return 5;
        return 0;
    }
    function scoreFromRepetition(clicks) {
        const map = {};
        clicks.forEach((c) => {
            const key = `${c.path}:${c.text}`;
            map[key] = (map[key] || 0) + 1;
        });

        let score = 0;

        Object.values(map).forEach((count) => {
            if (count >= 3 && count < 6) score += 10; // interest
            if (count >= 6) score -= 10; // confusion
        });

        return score;
    }
    function scoreFromInteraction(clicks, durationSec) {
        const rate = clicks.length / Math.max(durationSec, 1);

        if (rate > 0.3) return 25;
        if (rate > 0.15) return 15;
        if (rate > 0.05) return 5;
        return 0;
    }
    function getSessionDuration(events, idleCutoffSec = 1800) {
        const times = events
            .map((e) => {
                if (e.time instanceof Date) return e.time.getTime();
                if (e.event_time) {
                    const t = new Date(e.event_time).getTime();
                    return isNaN(t) ? null : t;
                }
                return null;
            })
            .filter((t) => t !== null)
            .sort((a, b) => a - b);

        if (times.length < 2) return 0;

        let duration = 0;

        for (let i = 1; i < times.length; i++) {
            const delta = (times[i] - times[i - 1]) / 1000;
            if (delta <= idleCutoffSec) {
                duration += delta;
            }
        }

        return Math.floor(duration);
    }
    function scoreFromScroll(scrollEvents) {
        if (!scrollEvents.length) return 0;

        const max = Math.max(...scrollEvents.map((e) => e.value));

        if (max >= 100) return 30;
        if (max >= 75) return 20;
        if (max >= 50) return 10;
        return 0;
    }
    function renderFunnelChart(cl, cv) {
        clickRankingChart?.destroy();

        clickRankingChart = new Chart(clickRankingCanvas, {
            type: "bar",
            data: {
                labels: cl,
                datasets: [
                    {
                        data: cv,
                        backgroundColor: "#6366f1", // Indigo color
                        borderRadius: 4,
                        barThickness: 20,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { display: false },
                    },
                    y: {
                        grid: { display: false },
                    },
                },
            },
        });
    }
    /* ---------- helpers ---------- */
    function groupScrollEventsByPath(events) {
        const map = {};
        let paths = [];
        path = paths;
        events.forEach((e) => {
            let last = e.path || "";
            computeSucces =
                last.includes("success") ||
                last.includes("thank") ||
                last.includes("complete");
            paths.push(e.path);
            if (e.event_type !== "scroll") return;
            const path = e.path || "/";
            map[path] ??= [];
            map[path].push({
                time: new Date(e.event_time),
                value: e.value,
            });
        });
        return Object.entries(map).map(([path, events]) => ({ path, events }));
    }

    function groupClickEventsByPath(events) {
        const map = {};
        events.forEach((e) => {
            if (e.event_type !== "click") return;
            const path = e.path || "/";
            map[path] ??= [];
            map[path].push({
                time: new Date(e.event_time),
                text: e.click_target || "Click", // include clicked element text
            });
        });
        return Object.entries(map).map(([path, events]) => ({ path, events }));
    }
</script>

{#if loading}
    <div class="dashboard-container loading-state">
        <div class="loader"></div>
        <p class="loading-text">Analyzing session behavior…</p>
    </div>
{/if}
<div class="dashboard-container">
    <header class="header">
        <button class="btn-back" onclick={onback}>
            <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"><path d="m15 18-6-6 6-6" /></svg
            >
            <span>Back to Sessions</span>
        </button>
        <div class="lead-meta">
            <span class="lead-label">Lead</span>
            <span class="lead-id">{leadId}</span>
        </div>
        <div class="intent-wrapper">
            <span class="label">Intent Score</span>
            <div
                class="badge"
                style="color: {intentBadge.color}; background-color: {intentBadge.bg}; border-color: {intentBadge.color}33"
            >
                <span class="dot" style="background-color: {intentBadge.color}"
                ></span>
                {intentBadge.label} ({rScore}%)
            </div>
        </div>
        <div class="insight-card">
            <span class="insight-label">Key Insight</span>
            <p class="insight-text">{keyInsight}</p>
        </div>
    </header>
    <div class="card summary-card">
        <div class="summary-item">
            <span class="label">Pages</span>
            <span class="value">{summary.pages}</span>
        </div>

        <div class="summary-item">
            <span class="label">Time Spent</span>
            <span class="value">{summary.duration}s</span>
        </div>

        <div class="summary-item">
            <span class="label">Max Scroll</span>
            <span class="value">{summary.scroll}%</span>
        </div>

        <div class="summary-item">
            <span class="label">Clicks</span>
            <span class="value">{summary.clicks}</span>
        </div>
    </div>

    <div class="stats-grid">
        <div class="card chart-card main-graph">
            <div class="card-header">
                <h3>Session Timeline</h3>
                <span class="subtitle"
                    >Scroll depth & click interactions over time</span
                >
            </div>
            <div class="graph-container">
                <canvas bind:this={graphCanvas}></canvas>
            </div>
        </div>

        <div class="card chart-card ranking-graph">
            <div class="card-header">
                <h3>Click Targets</h3>
                <span class="subtitle">Most interacted elements</span>
            </div>
            <div class="ranking-container">
                <canvas bind:this={clickRankingCanvas}></canvas>
            </div>
        </div>
        <div class="card interaction-pages">
            <div class="card-header">
                <h3>Most Interacted Pages</h3>
                <span class="subtitle">Pages driving user engagement</span>
            </div>

            {#if mostInteractedPages.length}
                <ul class="page-list">
                    {#each mostInteractedPages as page}
                        <li>
                            <span class="path">{page.path}</span>
                            <span class="score">{page.score}</span>
                        </li>
                    {/each}
                </ul>
            {:else}
                <p class="empty">No interactions detected</p>
            {/if}
        </div>
    </div>
</div>

<style>
    .lead-meta {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .lead-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        font-weight: 700;
    }

    .lead-id {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
    }
    /* Reset & Fonts */
    .loading-state {
        height: 80vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    .loader {
        width: 36px;
        height: 36px;
        border: 3px solid #e5e7eb;
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 0.9s linear infinite;
    }

    .loading-text {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .interaction-pages {
        max-height: 300px;
    }

    .page-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .page-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px dashed #e5e7eb;
    }

    .page-list li:last-child {
        border-bottom: none;
    }

    .page-list .path {
        font-size: 0.85rem;
        color: #334155;
        font-weight: 500;
        max-width: 70%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .page-list .score {
        font-size: 0.8rem;
        font-weight: 700;
        color: #6366f1;
        background: #eef2ff;
        padding: 4px 10px;
        border-radius: 9999px;
    }

    .empty {
        font-size: 0.85rem;
        color: #94a3b8;
    }

    .insight-card {
        margin-top: 8px;
        padding: 12px 16px;
        background: #f1f5f9;
        border-radius: 12px;
        max-width: 280px;
    }

    .insight-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
    }

    .insight-text {
        margin-top: 4px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #334155;
    }

    :global(body) {
        background-color: #f8fafc;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            "Helvetica Neue", Arial, sans-serif;
        color: #1e293b;
        margin: 0;
    }
    .summary-card {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }

    .summary-item {
        text-align: center;
    }

    .summary-item .label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }

    .summary-item .value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
    }

    .dashboard-container {
        padding: 24px;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Header Styling */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 32px;
    }

    .btn-back {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }

    .btn-back:hover {
        background: #f1f5f9;
        color: #0f172a;
        border-color: #cbd5e1;
    }

    .intent-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
    }

    .intent-wrapper .label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 700;
    }

    .badge {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid transparent;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    /* Grid Layout */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 24px;
    }

    /* Card Styling */
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow:
            0 4px 6px -1px rgb(0 0 0 / 0.05),
            0 2px 4px -2px rgb(0 0 0 / 0.05);
        border: 1px solid #f1f5f9;
    }

    .card-header {
        margin-bottom: 20px;
    }

    .card h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #334155;
        font-weight: 600;
    }

    .card .subtitle {
        display: block;
        margin-top: 4px;
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* Chart Containers */
    .graph-container {
        height: 400px;
        width: 100%;
        position: relative;
    }

    .ranking-container {
        height: 300px;
        width: 100%;
        position: relative;
    }

    /* Desktop View */
    @media (min-width: 1024px) {
        .stats-grid {
            grid-template-columns: 2fr 1fr; /* 2:1 ratio for main chart vs ranking */
        }
    }
</style>
