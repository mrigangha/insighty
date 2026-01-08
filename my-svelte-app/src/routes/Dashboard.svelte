<script>
    import BarChart from "./dashboard/BarChart.svelte";
    import LeadDrop from "./dashboard/LeadDrop.svelte";
    import PieChart from "./dashboard/PieChart.svelte";

    // ... (Your existing analytics logic remains exactly the same) ...
    const { leads } = $props();

    const analytics = $derived.by(() => {
        if (!leads || leads.length === 0) return null;
        // ... (keep logic exactly as before) ...
        // Total leads
        const total = leads.length;
        const dates = leads.map((l) => new Date(l.created_at));
        const sortedDates = dates
            .filter((d) => !isNaN(d))
            .sort((a, b) => a - b);
        const firstDate = sortedDates[0];
        const lastDate = sortedDates[sortedDates.length - 1];
        const daysDiff =
            Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24)) || 1;
        const avgPerDay = (total / daysDiff).toFixed(1);
        const now = new Date();
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const fourteenDaysAgo = new Date(
            now.getTime() - 14 * 24 * 60 * 60 * 1000,
        );
        const lastWeek = leads.filter((l) => {
            const d = new Date(l.date || l.createdAt || l.timestamp);
            return d >= sevenDaysAgo && d <= now;
        }).length;
        const previousWeek = leads.filter((l) => {
            const d = new Date(l.date || l.createdAt || l.timestamp);
            return d >= fourteenDaysAgo && d < sevenDaysAgo;
        }).length;
        const weeklyChange =
            previousWeek > 0
                ? (((lastWeek - previousWeek) / previousWeek) * 100).toFixed(1)
                : lastWeek > 0
                  ? 100
                  : 0;
        const sources = leads.reduce((acc, lead) => {
            const source = lead.source || lead.channel || "Unknown";
            acc[source] = (acc[source] || 0) + 1;
            return acc;
        }, {});
        const topSource = Object.entries(sources).sort(
            (a, b) => b[1] - a[1],
        )[0];
        const sourceCount = Object.keys(sources).length;
        const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        const dayDistribution = leads.reduce((acc, lead) => {
            const d = new Date(lead.date || lead.createdAt || lead.timestamp);
            if (!isNaN(d)) {
                const day = dayNames[d.getDay()];
                acc[day] = (acc[day] || 0) + 1;
            }
            return acc;
        }, {});
        const busiestDay = Object.entries(dayDistribution).sort(
            (a, b) => b[1] - a[1],
        )[0];

        return {
            total,
            avgPerDay,
            lastWeek,
            previousWeek,
            weeklyChange,
            topSource: topSource
                ? {
                      name: topSource[0],
                      count: topSource[1],
                      percentage: ((topSource[1] / total) * 100).toFixed(1),
                  }
                : null,
            sourceCount,
            busiestDay: busiestDay
                ? { day: busiestDay[0], count: busiestDay[1] }
                : null,
            daysDiff,
        };
    });
</script>

<section class="dashboard">
    <header class="dashboard-header">
        <div class="header-text">
            <h1>Lead Analytics</h1>
            <p>Overview of lead performance and distribution</p>
        </div>
    </header>

    {#if analytics}
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon blue">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><path
                            d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
                        /><circle cx="9" cy="7" r="4" /><path
                            d="M22 21v-2a4 4 0 0 0-3-3.87"
                        /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg
                    >
                </div>
                <div class="kpi-content">
                    <div class="kpi-label">Total Leads</div>
                    <div class="kpi-value">{analytics.total}</div>
                    <div class="kpi-subtitle">
                        Over {analytics.daysDiff} days
                    </div>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-icon purple">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><rect
                            x="3"
                            y="4"
                            width="18"
                            height="18"
                            rx="2"
                            ry="2"
                        /><line x1="16" y1="2" x2="16" y2="6" /><line
                            x1="8"
                            y1="2"
                            x2="8"
                            y2="6"
                        /><line x1="3" y1="10" x2="21" y2="10" /></svg
                    >
                </div>
                <div class="kpi-content">
                    <div class="kpi-label">Daily Avg</div>
                    <div class="kpi-value">{analytics.avgPerDay}</div>
                    <div class="kpi-subtitle">Leads / day</div>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-icon green">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><polyline
                            points="23 6 13.5 15.5 8.5 10.5 1 18"
                        /><polyline points="17 6 23 6 23 12" /></svg
                    >
                </div>
                <div class="kpi-content">
                    <div class="kpi-label">Weekly Trend</div>
                    <div class="trend-wrapper">
                        <span
                            class="trend-badge {analytics.weeklyChange >= 0
                                ? 'positive'
                                : 'negative'}"
                        >
                            {analytics.weeklyChange > 0
                                ? "+"
                                : ""}{analytics.weeklyChange}%
                        </span>
                    </div>
                    <div class="kpi-subtitle">vs. previous week</div>
                </div>
            </div>

            {#if analytics.topSource}
                <div class="kpi-card">
                    <div class="kpi-icon orange">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            ><circle cx="12" cy="12" r="10" /><circle
                                cx="12"
                                cy="12"
                                r="6"
                            /><circle cx="12" cy="12" r="2" /></svg
                        >
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-label">Top Source</div>
                        <div
                            class="kpi-value small text-truncate"
                            title={analytics.topSource.name}
                        >
                            {analytics.topSource.name}
                        </div>
                        <div class="kpi-subtitle">
                            {analytics.topSource.percentage}% of total
                        </div>
                    </div>
                </div>
            {/if}

            {#if analytics.busiestDay}
                <div class="kpi-card">
                    <div class="kpi-icon pink">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            ><circle cx="12" cy="12" r="10" /><polyline
                                points="12 6 12 12 16 14"
                            /></svg
                        >
                    </div>
                    <div class="kpi-content">
                        <div class="kpi-label">Busiest Day</div>
                        <div class="kpi-value small">
                            {analytics.busiestDay.day}
                        </div>
                        <div class="kpi-subtitle">
                            {analytics.busiestDay.count} leads
                        </div>
                    </div>
                </div>
            {/if}

            <div class="kpi-card">
                <div class="kpi-icon teal">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><polygon points="12 2 2 7 12 12 22 7 12 2" /><polyline
                            points="2 17 12 22 22 17"
                        /><polyline points="2 12 12 17 22 12" /></svg
                    >
                </div>
                <div class="kpi-content">
                    <div class="kpi-label">Sources</div>
                    <div class="kpi-value">{analytics.sourceCount}</div>
                    <div class="kpi-subtitle">Active channels</div>
                </div>
            </div>
        </div>
    {/if}

    <div class="charts-row">
        <div class="card chart-card">
            <div class="card-header">
                <h3>Leads Over Time</h3>
            </div>
            <div class="card-body">
                <BarChart {leads} />
            </div>
        </div>
        <div class="card chart-card">
            <div class="card-header">
                <h3>Lead Sources</h3>
            </div>
            <div class="card-body">
                <PieChart {leads} />
            </div>
        </div>
    </div>

    <div class="details-row">
        <div class="card full-width">
            <div class="card-header">
                <h3>Lead Details</h3>
            </div>
            <div class="card-body no-padding">
                <LeadDrop {leads} />
            </div>
        </div>
    </div>
</section>

<style>
    /* --- Variables for Easy Theming --- */
    :root {
        --bg-page: #f8fafc;
        --bg-card: #ffffff;
        --border-subtle: #e2e8f0;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --text-tertiary: #94a3b8;

        --color-blue-bg: #eff6ff;
        --color-blue-text: #3b82f6;
        --color-purple-bg: #f3e8ff;
        --color-purple-text: #a855f7;
        --color-green-bg: #dcfce7;
        --color-green-text: #22c55e;
        --color-red-bg: #fee2e2;
        --color-red-text: #ef4444;
        --color-orange-bg: #ffedd5;
        --color-orange-text: #f97316;
        --color-pink-bg: #fce7f3;
        --color-pink-text: #ec4899;
        --color-teal-bg: #ccfbf1;
        --color-teal-text: #14b8a6;
    }

    /* --- Layout & Typography --- */
    .dashboard {
        padding: 2rem;
        background: var(--bg-page);
        min-height: 100vh;
        font-family:
            "Inter",
            system-ui,
            -apple-system,
            sans-serif;
        color: var(--text-primary);
    }

    .dashboard-header {
        margin-bottom: 2rem;
    }
    .dashboard-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
    }
    .dashboard-header p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0;
    }

    /* --- KPI Grid --- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        transition:
            transform 0.2s,
            box-shadow 0.2s;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 10px 15px -3px rgba(0, 0, 0, 0.05),
            0 4px 6px -2px rgba(0, 0, 0, 0.025);
        border-color: #cbd5e1;
    }

    /* Icons and Content */
    .kpi-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .kpi-icon.blue {
        background: var(--color-blue-bg);
        color: var(--color-blue-text);
    }
    .kpi-icon.purple {
        background: var(--color-purple-bg);
        color: var(--color-purple-text);
    }
    .kpi-icon.green {
        background: var(--color-green-bg);
        color: var(--color-green-text);
    }
    .kpi-icon.orange {
        background: var(--color-orange-bg);
        color: var(--color-orange-text);
    }
    .kpi-icon.pink {
        background: var(--color-pink-bg);
        color: var(--color-pink-text);
    }
    .kpi-icon.teal {
        background: var(--color-teal-bg);
        color: var(--color-teal-text);
    }

    .kpi-content {
        display: flex;
        flex-direction: column;
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -0.025em;
    }
    .kpi-value.small {
        font-size: 1.4rem;
    }
    .text-truncate {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .kpi-subtitle {
        font-size: 0.8rem;
        color: var(--text-tertiary);
        margin-top: 0.25rem;
    }

    /* Trend Badges */
    .trend-wrapper {
        margin: 4px 0;
    }
    .trend-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .trend-badge.positive {
        background: var(--color-green-bg);
        color: var(--color-green-text);
    }
    .trend-badge.negative {
        background: var(--color-red-bg);
        color: var(--color-red-text);
    }

    /* --- CHART LAYOUT (NEW) --- */

    /* Dedicated row for the two graphs */
    .charts-row {
        display: grid;
        /* Force 2 equal columns */
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Container for the Full Width Table */
    .details-row {
        display: flex;
        width: 100%;
    }

    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        width: 100%; /* Ensure cards take full space of their grid cell */
    }

    .card-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid var(--border-subtle);
        background-color: #fbfcfd;
    }
    .card-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
    }
    .card-body {
        padding: 1.5rem;
    }
    .card-body.no-padding {
        padding: 0;
    }

    /* --- Responsive --- */
    @media (max-width: 900px) {
        /* On tablets/mobile, stack the charts vertically */
        .charts-row {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .dashboard {
            padding: 1rem;
        }
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 480px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
