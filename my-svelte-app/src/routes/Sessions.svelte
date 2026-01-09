<script>
    import { onMount } from "svelte";
    import { push } from "svelte-spa-router";
    import {
        getLoggedIn,
        getOpenProjectId,
        URL,
        getOpenSessionLeadId,
        getOpenSessionId,
        setOpenSessionId,
        setOpenSessionLeadId,
        getDirectOpenSession,
        setDirectOpenSession,
        getLeadVisitorId,
        setLeadVisitorId,
        getAccessToken,
    } from "../lib/store.svelte";
    import SessionData from "./SessionData.svelte";
    import { get } from "svelte/store";

    let projectId = $derived(getOpenProjectId());
    let sessions = $state([]);
    let isLoading = $state(true); // Added for UI feedback

    async function DeleteSession(sessionId) {
        const token = getAccessToken();
        if (!token) {
            push("/profile");
            return;
        }

        const response = await fetch(
            `${URL}/session/${projectId}/${sessionId}`,
            {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            },
        );
        if (!response.ok) {
            alert("Unable to delete");
            return;
        }
        sessions = sessions.filter((session) => session.id !== sessionId);
    }

    onMount(async () => {
        setOpenSessionId(-1);
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
            const response = await fetch(`${URL}/sessions/${projectId}/`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                alert("Unable to fetch");
                return;
            }
            const data = await response.json();
            sessions = data["sessions"];
            if (getDirectOpenSession()) {
                for (let i = 0; i < sessions.length; i++) {
                    if (sessions[i].id === getLeadVisitorId()) {
                        openSession(sessions[i].id, sessions[i].session_id);
                        setLeadVisitorId(-1);
                    }
                }
            }
        } finally {
            isLoading = false;
        }
    });

    function openSession(index, leadId) {
        setOpenSessionId(index); // Keeping your original logic
        setOpenSessionLeadId(leadId);
    }

    function showSession() {
        setOpenSessionId(-1);
        setOpenSessionLeadId("");
    }

    /* Helper for date formatting */
    function formatDate(dateString) {
        if (!dateString) return "-";
        return new Date(dateString).toLocaleString(undefined, {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }
</script>

{#if getOpenSessionId() === -1}
    <div class="container">
        <header class="page-header">
            <div>
                <h1>Project Sessions</h1>
                <p class="subtitle">Manage and view recorded user sessions</p>
            </div>
            <div class="badge">
                {sessions.length} Records
            </div>
        </header>

        <div class="card">
            <div class="table-header">
                <div class="col-id">Session ID</div>
                <div class="col-date">Created At</div>
                <div class="col-action">Actions</div>
            </div>

            <div class="table-body">
                {#if isLoading}
                    <div class="empty-state">Loading sessions...</div>
                {:else if sessions.length === 0}
                    <div class="empty-state">
                        <p>No sessions found for this project.</p>
                    </div>
                {:else}
                    {#each sessions as session, index}
                        <div
                            class="row"
                            onclick={() =>
                                openSession(session.id, session.session_id)}
                        >
                            <div class="col-id">
                                <span class="id-tag">{session.session_id}</span>
                            </div>
                            <div class="col-date">
                                {formatDate(session.created_at)}
                            </div>
                            <div class="col-action">
                                <button
                                    class="btn-delete"
                                    title="Delete Session"
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        DeleteSession(session.id);
                                    }}
                                >
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        ><path d="M3 6h18" /><path
                                            d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"
                                        /><path
                                            d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"
                                        /></svg
                                    >
                                    Delete
                                </button>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
{:else}
    <SessionData
        onback={showSession}
        SessionId={getOpenSessionId()}
        leadId={getOpenSessionLeadId()}
    />
{/if}

<style>
    /* Global Reset Match */
    :global(body) {
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            "Helvetica Neue", Arial, sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    /* Header Styling */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 24px;
    }

    .page-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
    }

    .subtitle {
        margin: 4px 0 0 0;
        color: #64748b;
        font-size: 0.95rem;
    }

    .badge {
        background: #e2e8f0;
        color: #475569;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 999px;
    }

    /* Card/Table Styling */
    .card {
        background: white;
        border-radius: 12px;
        box-shadow:
            0 4px 6px -1px rgb(0 0 0 / 0.05),
            0 2px 4px -2px rgb(0 0 0 / 0.05);
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }

    .table-header {
        display: grid;
        grid-template-columns: 2fr 1.5fr 100px; /* Fixed width for actions */
        padding: 16px 24px;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
    }

    .row {
        display: grid;
        grid-template-columns: 2fr 1.5fr 100px;
        padding: 16px 24px;
        align-items: center;
        border-bottom: 1px solid #f1f5f9;
        transition: background-color 0.2s;
        cursor: pointer;
    }

    .row:last-child {
        border-bottom: none;
    }

    .row:hover {
        background-color: #f1f5f9;
    }

    /* Columns */
    .col-id {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        padding-right: 16px;
    }

    .id-tag {
        font-family:
            "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        color: #334155;
        font-size: 0.9rem;
    }

    .col-date {
        color: #64748b;
        font-size: 0.9rem;
    }

    .col-action {
        text-align: right;
    }

    /* Buttons */
    .btn-delete {
        display: flex;
        align-items: center;
        gap: 6px;
        background: transparent;
        color: #ef4444;
        border: 1px solid #fee2e2;
        padding: 6px 12px;
        font-size: 0.85rem;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-delete:hover {
        background: #fee2e2;
        border-color: #fecaca;
    }

    /* Empty State */
    .empty-state {
        padding: 48px;
        text-align: center;
        color: #94a3b8;
    }
</style>
