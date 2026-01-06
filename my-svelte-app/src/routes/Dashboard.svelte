<script>
    import BarChart from "./dashboard/BarChart.svelte";
    import LeadDrop from "./dashboard/LeadDrop.svelte";
    import PieChart from "./dashboard/PieChart.svelte";
    const { leads } = $props();

    // Derived analytics from existing leads data
    const analytics = $derived.by(() => {
        if (!leads || leads.length === 0) return null;

        // Total leads
        const total = leads.length;
        // Date-based analysis
        const dates = leads.map((l) => new Date(l.created_at));
        const sortedDates = dates
            .filter((d) => !isNaN(d))
            .sort((a, b) => a - b);

        // Time range
        const firstDate = sortedDates[0];
        const lastDate = sortedDates[sortedDates.length - 1];
        const daysDiff =
            Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24)) || 1;

        // Average per day
        const avgPerDay = (total / daysDiff).toFixed(1);

        // Recent trends (last 7 days vs previous 7 days)
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

        // Source analysis
        const sources = leads.reduce((acc, lead) => {
            const source = lead.source || lead.channel || "Unknown";
            acc[source] = (acc[source] || 0) + 1;
            return acc;
        }, {});

        const topSource = Object.entries(sources).sort(
            (a, b) => b[1] - a[1],
        )[0];

        const sourceCount = Object.keys(sources).length;

        // Day of week analysis
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
        <h1>Lead Analytics</h1>
        <p>Overview of lead performance and distribution</p>
    </header>

    {#if analytics}
        <!-- New KPI Cards Section -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Leads</div>
                <div class="kpi-value">{analytics.total}</div>
                <div class="kpi-subtitle">
                    {analytics.daysDiff} days tracked
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Daily Average</div>
                <div class="kpi-value">{analytics.avgPerDay}</div>
                <div class="kpi-subtitle">leads per day</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Weekly Trend</div>
                <div
                    class="kpi-value trend {analytics.weeklyChange >= 0
                        ? 'positive'
                        : 'negative'}"
                >
                    {analytics.weeklyChange > 0
                        ? "+"
                        : ""}{analytics.weeklyChange}%
                </div>
                <div class="kpi-subtitle">
                    {analytics.lastWeek} this week vs {analytics.previousWeek} last
                    week
                </div>
            </div>

            {#if analytics.topSource}
                <div class="kpi-card">
                    <div class="kpi-label">Top Source</div>
                    <div class="kpi-value small">
                        {analytics.topSource.name}
                    </div>
                    <div class="kpi-subtitle">
                        {analytics.topSource.percentage}% ({analytics.topSource
                            .count} leads)
                    </div>
                </div>
            {/if}

            {#if analytics.busiestDay}
                <div class="kpi-card">
                    <div class="kpi-label">Busiest Day</div>
                    <div class="kpi-value small">
                        {analytics.busiestDay.day}
                    </div>
                    <div class="kpi-subtitle">
                        {analytics.busiestDay.count} leads
                    </div>
                </div>
            {/if}

            <div class="kpi-card">
                <div class="kpi-label">Lead Sources</div>
                <div class="kpi-value">{analytics.sourceCount}</div>
                <div class="kpi-subtitle">active channels</div>
            </div>
        </div>
    {/if}

    <!-- Existing Charts - Unchanged -->
    <div class="chart-container">
        <div class="card">
            <h3>Leads Over Time</h3>
            <BarChart {leads} />
        </div>
        <div class="card">
            <h3>Lead Sources</h3>
            <PieChart {leads} />
        </div>
    </div>

    <!-- Existing Lead Details - Unchanged -->
    <div class="card full-width">
        <h3>Lead Details</h3>
        <LeadDrop {leads} />
    </div>
</section>

<style>
    /* Page */
    .dashboard {
        padding: 1.5rem;
        background: #f8fafc;
        min-height: 100vh;
        font-family: system-ui, sans-serif;
    }

    /* Header */
    .dashboard-header {
        margin-bottom: 1.5rem;
    }
    .dashboard-header h1 {
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .dashboard-header p {
        color: #64748b;
        font-size: 0.9rem;
    }

    /* NEW: KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
    }

    .kpi-card:nth-child(2) {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.25);
    }

    .kpi-card:nth-child(2):hover {
        box-shadow: 0 8px 20px rgba(240, 147, 251, 0.35);
    }

    .kpi-card:nth-child(3) {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.25);
    }

    .kpi-card:nth-child(3):hover {
        box-shadow: 0 8px 20px rgba(79, 172, 254, 0.35);
    }

    .kpi-card:nth-child(4) {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        box-shadow: 0 4px 12px rgba(67, 233, 123, 0.25);
    }

    .kpi-card:nth-child(4):hover {
        box-shadow: 0 8px 20px rgba(67, 233, 123, 0.35);
    }

    .kpi-card:nth-child(5) {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 4px 12px rgba(250, 112, 154, 0.25);
    }

    .kpi-card:nth-child(5):hover {
        box-shadow: 0 8px 20px rgba(250, 112, 154, 0.35);
    }

    .kpi-card:nth-child(6) {
        background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        box-shadow: 0 4px 12px rgba(48, 207, 208, 0.25);
    }

    .kpi-card:nth-child(6):hover {
        box-shadow: 0 8px 20px rgba(48, 207, 208, 0.35);
    }

    .kpi-label {
        font-size: 0.75rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        line-height: 1;
    }

    .kpi-value.small {
        font-size: 1.5rem;
    }

    .kpi-value.trend {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .kpi-value.positive::before {
        content: "↑";
        font-size: 1.5rem;
    }

    .kpi-value.negative::before {
        content: "↓";
        font-size: 1.5rem;
    }

    .kpi-subtitle {
        font-size: 0.8rem;
        opacity: 0.85;
    }

    /* Charts layout */
    .chart-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 1.25rem;
        margin-bottom: 1.25rem;
    }

    /* Card */
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    }
    .card h3 {
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
        color: #0f172a;
    }
    .full-width {
        grid-column: 1 / -1;
    }

    /* Mobile */
    @media (max-width: 640px) {
        .dashboard {
            padding: 1rem;
        }
        .kpi-grid {
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        }
        .kpi-value {
            font-size: 1.5rem;
        }
    }
</style>
