<script>
    import { onMount } from "svelte";
    import {
        getLeadVisitorId,
        getLoggedIn,
        setDirectOpenSession,
        setLeadVisitorId,
        setOpenSessionLeadId,
    } from "../lib/store.svelte";
    import {
        URL,
        getOpenProjectId,
        getOpenProjectName,
        getAccessToken,
    } from "../lib/store.svelte";
    import { push } from "svelte-spa-router";
    import Dashboard from "./Dashboard.svelte";
    import Pipeline from "./Pipeline.svelte";
    import Sessions from "./Sessions.svelte";
    import Settings from "./Settings.svelte";

    let leads = $state({ leads: [] }); // Initialize structure to avoid undefined errors
    let edit = $state(false);
    let editIndex = $state(-1);
    let addLead = $state(false);

    // UI Loading state
    let isLoading = $state(true);

    let updatedLead = $state({
        name: "",
        email: "",
        phone: "",
        source: "",
        status: "",
        id: "",
    });

    let newLead = $state({
        name: "",
        email: "",
        phone: "",
        source: "",
        status: "NEW",
    });

    let projectId = $derived(getOpenProjectId());

    const pageViews = {
        LEADS: "Leads",
        DASHBOARD: "Dashboard",
        PIPELINE: "Pipeline",
        SESSION: "Session",
        SETTINGS: "Settings",
    };

    let currentView = $state(pageViews.LEADS);

    // Format date helper
    function formatDate(dateString) {
        if (!dateString) return "—";
        const date = new Date(dateString);
        return new Intl.DateTimeFormat("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        }).format(date);
    }

    async function attachSessionToLead(leadId, index) {
        const sessionId = prompt("Enter Session ID to link:");
        if (!sessionId) return;

        const token = getAccessToken();
        if (!token) {
            push("/profile");
            return;
        }

        const res = await fetch(
            `${URL}/leads/${leadId}/attach-session/${sessionId}`,
            {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            },
        );

        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || "Failed to link session");
            return;
        }
        console.log(data["visitor_session_id"]);
        console.log(leads);
        leads.leads[index] = {
            ...leads.leads[index],
            visitor_session_id: data.visitor_session_id,
        };
    }

    onMount(async () => {
        if (!getLoggedIn()) {
            push("/login");
            return;
        }
        const token = getAccessToken();
        if (!token) {
            push("/profile");
            return;
        }

        try {
            const response = await fetch(`${URL}/leads/${projectId}/leads`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                // Handle specific error codes if needed
                return;
            }
            leads = await response.json();
            console.log(leads);
        } catch (e) {
            console.error(e);
        } finally {
            isLoading = false;
        }
    });

    // Helper for Status Colors
    function getStatusClass(status) {
        switch (status) {
            case "WON":
                return "badge-success";
            case "LOST":
                return "badge-danger";
            case "IN_PROGRESS":
                return "badge-warning";
            default:
                return "badge-neutral";
        }
    }

    // Helper icons
    const Icons = {
        Leads: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
        Dashboard: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>`,
        Pipeline: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>`,
        Session: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`,
        Settings: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
    };
</script>

<div class="main-layout">
    <aside class="sidebar">
        <div class="brand">
            <div class="project-name">{getOpenProjectName()}</div>
            <div class="project-label">Project Workspace</div>
        </div>

        <nav class="nav-menu">
            {#each Object.entries(pageViews) as [key, label]}
                <button
                    class:active={currentView === label}
                    onclick={() => (currentView = label)}
                >
                    {@html Icons[key] || ""}
                    {label}
                </button>
            {/each}
        </nav>

        <div class="user-profile"></div>
    </aside>

    <main class="content-area">
        {#if currentView === pageViews.LEADS}
            <div class="view-container">
                <header class="view-header">
                    <div>
                        <h1>Lead Management</h1>
                        <p class="subtitle">
                            Track and manage potential customers
                        </p>
                    </div>
                    <div class="header-actions">
                        <button
                            class="btn-secondary"
                            onclick={async () => {
                                const token = getAccessToken();
                                if (token) {
                                    const res = await fetch(
                                        `${URL}/leads/${projectId}/leads`,
                                        {
                                            headers: {
                                                Authorization: `Bearer ${token}`,
                                            },
                                        },
                                    );
                                    if (res.ok) leads = await res.json();
                                }
                            }}
                        >
                            Refresh
                        </button>
                        <button
                            class="btn-primary"
                            onclick={() => (addLead = !addLead)}
                        >
                            {addLead ? "Close Form" : "+ Add New Lead"}
                        </button>
                    </div>
                </header>

                {#if addLead}
                    <div class="form-panel">
                        <h3>Add New Lead</h3>
                        <div class="form-grid">
                            <input
                                type="text"
                                bind:value={newLead.name}
                                placeholder="Name"
                                class="input-field"
                            />
                            <input
                                type="email"
                                bind:value={newLead.email}
                                placeholder="Email"
                                class="input-field"
                            />
                            <input
                                type="tel"
                                bind:value={newLead.phone}
                                placeholder="Phone"
                                class="input-field"
                            />
                            <input
                                type="text"
                                bind:value={newLead.source}
                                placeholder="Source (e.g. LinkedIn)"
                                class="input-field"
                            />
                            <select
                                bind:value={newLead.status}
                                class="input-field"
                            >
                                <option value="NEW">New</option>
                                <option value="IN_PROGRESS">In Progress</option>
                                <option value="WON">Won</option>
                                <option value="LOST">Lost</option>
                            </select>
                        </div>
                        <div class="form-actions">
                            <button
                                class="btn-text"
                                onclick={() => (addLead = false)}>Cancel</button
                            >
                            <button
                                class="btn-primary"
                                onclick={async () => {
                                    const token = getAccessToken();
                                    if (!token) return push("/profile");
                                    const response = await fetch(
                                        `${URL}/lead`,
                                        {
                                            method: "POST",
                                            headers: {
                                                "Content-Type":
                                                    "application/json",
                                                Authorization: `Bearer ${token}`,
                                            },
                                            body: JSON.stringify({
                                                ...newLead,
                                                project_id: projectId,
                                            }),
                                        },
                                    );
                                    if (response.ok) {
                                        const data = await response.json();
                                        leads["leads"] = [
                                            ...leads["leads"],
                                            {
                                                id: data["lead_id"],
                                                ...newLead,
                                                created_at:
                                                    new Date().toISOString(),
                                            },
                                        ];
                                        addLead = false;
                                        newLead = {
                                            name: "",
                                            email: "",
                                            phone: "",
                                            source: "",
                                            status: "NEW",
                                        };
                                    } else {
                                        alert("Failed");
                                    }
                                }}>Save Lead</button
                            >
                        </div>
                    </div>
                {/if}

                <div class="card table-card">
                    <div class="table-header-row">
                        <div class="col col-name">Name</div>
                        <div class="col col-email">Contact Info</div>
                        <div class="col col-source">Source</div>
                        <div class="col col-status">Status</div>
                        <div class="col col-date">Created</div>
                        <div class="col col-actions"></div>
                    </div>

                    {#if isLoading}
                        <div class="empty-state">Loading leads...</div>
                    {:else if leads["leads"].length === 0}
                        <div class="empty-state">
                            No leads found. Add one to get started!
                        </div>
                    {:else}
                        {#each leads["leads"] as lead, index}
                            <div class="table-row">
                                {#if edit && editIndex === index}
                                    <div class="col col-name">
                                        <input
                                            type="text"
                                            bind:value={updatedLead.name}
                                            class="input-sm"
                                        />
                                    </div>
                                    <div class="col col-email">
                                        <input
                                            type="email"
                                            bind:value={updatedLead.email}
                                            placeholder="Email"
                                            class="input-sm mb-1"
                                        />
                                        <input
                                            type="tel"
                                            bind:value={updatedLead.phone}
                                            placeholder="Phone"
                                            class="input-sm"
                                        />
                                    </div>
                                    <div class="col col-source">
                                        <input
                                            type="text"
                                            bind:value={updatedLead.source}
                                            class="input-sm"
                                        />
                                    </div>
                                    <div class="col col-status">
                                        <select
                                            bind:value={updatedLead.status}
                                            class="input-sm"
                                        >
                                            <option value="NEW">New</option>
                                            <option value="IN_PROGRESS"
                                                >In Progress</option
                                            >
                                            <option value="WON">Won</option>
                                            <option value="LOST">Lost</option>
                                        </select>
                                    </div>
                                    <div class="col col-date">
                                        <span class="date-text"
                                            >{formatDate(lead.created_at)}</span
                                        >
                                    </div>
                                    <div class="col col-actions action-buttons">
                                        <button
                                            class="btn-icon save"
                                            onclick={async () => {
                                                const token = getAccessToken();
                                                if (!token)
                                                    return push("/profile");
                                                const res = await fetch(
                                                    `${URL}/leads/${projectId}/${updatedLead.id}`,
                                                    {
                                                        method: "PATCH",
                                                        headers: {
                                                            "Content-Type":
                                                                "application/json",
                                                            Authorization: `Bearer ${token}`,
                                                        },
                                                        body: JSON.stringify(
                                                            updatedLead,
                                                        ),
                                                    },
                                                );
                                                if (res.ok) {
                                                    leads["leads"][index] =
                                                        updatedLead;
                                                    edit = false;
                                                    editIndex = -1;
                                                }
                                            }}>Save</button
                                        >
                                        <button
                                            class="btn-icon cancel"
                                            onclick={() => {
                                                edit = false;
                                                editIndex = -1;
                                            }}>Cancel</button
                                        >
                                    </div>
                                {:else}
                                    <div class="col col-name">
                                        <span class="name-text"
                                            >{lead.name}</span
                                        >
                                    </div>
                                    <div class="col col-email">
                                        <div class="email-text">
                                            {lead.email}
                                        </div>
                                        <div class="phone-text">
                                            {lead.phone}
                                        </div>
                                    </div>
                                    <div class="col col-source">
                                        <span class="source-tag"
                                            >{lead.source}</span
                                        >
                                    </div>
                                    <div class="col col-status">
                                        <span
                                            class="badge {getStatusClass(
                                                lead.status,
                                            )}"
                                        >
                                            {lead.status.replace("_", " ")}
                                        </span>
                                    </div>
                                    <div class="col col-date">
                                        <span class="date-text"
                                            >{formatDate(lead.created_at)}</span
                                        >
                                    </div>
                                    <div class="col col-actions action-buttons">
                                        <button
                                            class={`btn-icon link ${
                                                lead.visitor_session_id
                                                    ? "linked"
                                                    : "unlinked"
                                            }`}
                                            title={lead.visitor_session_id
                                                ? "Session linked"
                                                : "Link session"}
                                            onclick={() => {
                                                if (!lead.visitor_session_id) {
                                                    attachSessionToLead(
                                                        lead.id,
                                                        index,
                                                    );
                                                } else {
                                                    setDirectOpenSession(true);
                                                    currentView =
                                                        pageViews.SESSION;

                                                    setLeadVisitorId(
                                                        lead.visitor_session_id,
                                                    );
                                                }
                                            }}
                                        >
                                            🔗
                                        </button>
                                        <button
                                            class="btn-icon edit"
                                            onclick={() => {
                                                edit = true;
                                                editIndex = index;
                                                updatedLead = { ...lead };
                                            }}
                                        >
                                            Edit
                                        </button>
                                        <button
                                            class="btn-icon delete"
                                            onclick={async () => {
                                                if (!confirm("Are you sure?"))
                                                    return;
                                                const token = getAccessToken();
                                                if (!token)
                                                    return push("/profile");
                                                const res = await fetch(
                                                    `${URL}/leads/${projectId}/${lead.id}`,
                                                    {
                                                        method: "DELETE",
                                                        headers: {
                                                            "Content-Type":
                                                                "application/json",
                                                            Authorization: `Bearer ${token}`,
                                                        },
                                                    },
                                                );
                                                if (res.ok)
                                                    leads["leads"] = leads[
                                                        "leads"
                                                    ].filter(
                                                        (_, i) => i !== index,
                                                    );
                                            }}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        {:else if currentView === pageViews.DASHBOARD}
            <div class="view-container">
                <Dashboard leads={$state.snapshot(leads["leads"])} />
            </div>
        {:else if currentView === pageViews.PIPELINE}
            <div class="view-container">
                <Pipeline />
            </div>
        {:else if currentView === pageViews.SESSION}
            <div class="view-container">
                <Sessions />
            </div>
        {:else if currentView === pageViews.SETTINGS}
            <div class="view-container">
                <Settings />
            </div>
        {/if}
    </main>
</div>

<style>
    /* Global Reset & Base */
    button.link {
        transition: all 0.2s ease;
    }

    button.unlinked {
        background: #e5e7eb;
        color: #6b7280;
    }

    button.unlinked:hover {
        background: #d1d5db;
    }

    button.linked {
        background: #dcfce7;
        color: #166534;
        cursor: default;
    }
    :global(body) {
        margin: 0;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
            Arial, sans-serif;
        background-color: #f8fafc;
        color: #334155;
    }

    .main-layout {
        display: flex;
        min-height: 100vh;
    }

    /* --- Sidebar Styles --- */
    .sidebar {
        width: 240px;
        background-color: #0f172a; /* Dark Navy */
        color: #e2e8f0;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        height: 100vh;
        overflow: hidden;
        position: sticky;
        top: 0;
    }

    .brand {
        padding: 24px 20px;
        border-bottom: 1px solid #1e293b;
    }
    .project-name {
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
    }
    .project-label {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .nav-menu {
        padding: 20px 10px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .nav-menu button {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        padding: 10px 16px;
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        text-align: left;
        font-size: 0.95rem;
        transition: all 0.2s;
    }

    .nav-menu button:hover {
        background-color: #1e293b;
        color: white;
    }

    .nav-menu button.active {
        background-color: #2563eb; /* Primary Blue */
        color: white;
    }

    /* --- Content Area --- */
    .content-area {
        flex: 1;
        overflow-y: auto;
        background-color: #f1f5f9;
        height: 100vh;
    }

    .view-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 32px;
    }

    /* Header */
    .view-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 24px;
    }
    .view-header h1 {
        margin: 0;
        font-size: 1.8rem;
        color: #0f172a;
    }
    .subtitle {
        margin: 5px 0 0 0;
        color: #64748b;
    }
    .header-actions {
        display: flex;
        gap: 12px;
    }

    /* --- Form Panel --- */
    .form-panel {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        animation: slideDown 0.2s ease-out;
    }
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .form-panel h3 {
        margin-top: 0;
        margin-bottom: 16px;
        font-size: 1rem;
        color: #334155;
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }

    /* Inputs */
    .input-field,
    .input-sm {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font-size: 0.9rem;
        box-sizing: border-box;
    }
    .input-field:focus,
    .input-sm:focus {
        outline: 2px solid #2563eb;
        border-color: transparent;
    }
    .mb-1 {
        margin-bottom: 4px;
    }

    /* --- Table Card --- */
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        overflow: hidden;
    }

    .table-header-row {
        display: grid;
        grid-template-columns: 1.8fr 2.2fr 1.3fr 1.2fr 1.5fr 140px;
        padding: 12px 24px;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748b;
    }

    .table-row {
        display: grid;
        grid-template-columns: 1.8fr 2.2fr 1.3fr 1.2fr 1.5fr 140px;
        padding: 16px 24px;
        border-bottom: 1px solid #f1f5f9;
        align-items: center;
        transition: background-color 0.1s;
    }
    .table-row:last-child {
        border-bottom: none;
    }
    .table-row:hover {
        background-color: #f8fafc;
    }

    /* Table Columns Typography */
    .name-text {
        font-weight: 600;
        color: #0f172a;
    }
    .email-text {
        font-size: 0.9rem;
    }
    .phone-text {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 2px;
    }
    .source-tag {
        display: inline-block;
        background: #f1f5f9;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #475569;
    }

    .date-text {
        font-size: 0.85rem;
        color: #64748b;
        white-space: nowrap;
    }

    /* Status Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .badge-neutral {
        background: #e2e8f0;
        color: #475569;
    } /* NEW */
    .badge-warning {
        background: #fef3c7;
        color: #d97706;
    } /* IN PROGRESS */
    .badge-success {
        background: #dcfce7;
        color: #166534;
    } /* WON */
    .badge-danger {
        background: #fee2e2;
        color: #991b1b;
    } /* LOST */

    /* Buttons */
    .btn-primary {
        background: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
    }
    .btn-primary:hover {
        background: #1d4ed8;
    }

    .btn-secondary {
        background: white;
        color: #334155;
        border: 1px solid #cbd5e1;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
    }
    .btn-secondary:hover {
        background: #f8fafc;
        border-color: #94a3b8;
    }

    .btn-text {
        background: none;
        border: none;
        color: #64748b;
        cursor: pointer;
        padding: 8px 16px;
    }
    .btn-text:hover {
        color: #334155;
    }

    /* Action Buttons (Edit/Delete) */
    .action-buttons {
        text-align: right;
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }
    .btn-icon {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .edit {
        color: #2563eb;
    }
    .edit:hover {
        background: #eff6ff;
    }
    .delete {
        color: #ef4444;
    }
    .delete:hover {
        background: #fef2f2;
    }
    .save {
        color: #166534;
        background: #dcfce7;
    }
    .cancel {
        color: #64748b;
    }

    .empty-state {
        padding: 40px;
        text-align: center;
        color: #94a3b8;
    }
</style>
