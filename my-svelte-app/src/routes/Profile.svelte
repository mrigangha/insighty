<script>
    import { onMount } from "svelte";
    import { push } from "svelte-spa-router";
    import {
        getLoggedIn,
        setLoggedIn,
        URL,
        getAccessToken,
        setAccessToken,
        refreshAccessToken,
        setLoggedInUser,
        setPlan,
    } from "../lib/store.svelte";
    import defaultAvatar from "../assets/default.png";
    import { fade, fly, slide } from "svelte/transition";
    import { set } from "date-fns";

    let user = $state({ name: "", email: "", plan: "", original_plan: "" });
    let editUser = $state(false);
    let nameValue = $state("");

    let isSaving = $state(false);

    async function checkAuth() {
        let token = getAccessToken();
        if (!token) {
            let location = localStorage.getItem("location");
            const status = await refreshAccessToken();
            if (!status) {
                setLoggedInUser("", "");
                setLoggedIn(false);
                push("/logout");
                return null;
            }
        }
        return getAccessToken();
    }

    onMount(async () => {
        let token = await checkAuth();
        if (!token) {
            push("/login");
            return;
        }
        if (!getLoggedIn()) {
            push("/login");
            return;
        }

        try {
            let res = await fetch(`${URL}/profile`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            if (res.ok) {
                user = await res.json();
                nameValue = user.name;
                setLoggedInUser(user.name, user.email);
            } else {
                const status = await refreshAccessToken();
                if (!status) {
                    setLoggedIn(false);
                    push("/logout");
                    return null;
                }
                let token = await checkAuth();
                let res = await fetch(`${URL}/profile`, {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                });
                user = await res.json();

                nameValue = user.name;
                setLoggedInUser(user.name, user.email);
            }
        } catch (err) {
            console.error(err);
        }
    });

    async function updateUser() {
        const token = await checkAuth();
        if (!token || nameValue === user.name) {
            editUser = false;
            return;
        }

        isSaving = true;
        try {
            const res = await fetch(`${URL}/profile`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name: nameValue }),
            });
            if (res.ok) {
                user.name = nameValue;
                setLoggedInUser(user.name, user.email);
                editUser = false;
            } else {
                alert("Failed to update user");
            }
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="profile-page" in:fade>
    <div class="content-wrapper">
        {#if user.plan != user.original_plan}
            <div class="alert-banner" transition:slide>
                <div class="alert-icon">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        class="feather feather-alert-circle"
                    >
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                </div>
                <div class="alert-content">
                    <strong>Payment Pending</strong>
                    <p>
                        Your transaction for the <b>{user.plan}</b> plan was unsuccessful.
                    </p>
                </div>
                <button
                    class="retry-btn"
                    onclick={() => {
                        setPlan(user.original_plan);
                        push("/pay");
                    }}
                >
                    Retry Payment
                </button>
            </div>
        {/if}

        <div class="profile-card">
            <header class="card-header">
                <div class="avatar-container">
                    <img src={defaultAvatar} alt="User Avatar" />
                    <div class="status-badge"></div>
                </div>
                <h1>Account Settings</h1>
                <p>Manage your personal information</p>
            </header>

            <div class="settings-list">
                <div class="setting-item">
                    <div class="info full-width">
                        <label for="name">Full Name</label>
                        {#if editUser}
                            <div
                                class="input-wrapper"
                                in:fly={{ y: -5, duration: 200 }}
                            >
                                <input
                                    id="name"
                                    type="text"
                                    bind:value={nameValue}
                                    onkeydown={(e) =>
                                        e.key === "Enter" && updateUser()}
                                    autofocus
                                    placeholder="Enter your name"
                                />
                                <div class="input-actions">
                                    <button
                                        class="btn-icon btn-save"
                                        onclick={updateUser}
                                        disabled={isSaving}
                                        title="Save"
                                    >
                                        {#if isSaving}
                                            <span class="spinner"></span>
                                        {:else}
                                            ✓
                                        {/if}
                                    </button>
                                    <button
                                        class="btn-icon btn-cancel"
                                        onclick={() => {
                                            editUser = false;
                                            nameValue = user.name;
                                        }}
                                        title="Cancel"
                                    >
                                        ✕
                                    </button>
                                </div>
                            </div>
                        {:else}
                            <div class="display-value-row">
                                <p class="value">
                                    {user?.name || "Loading..."}
                                </p>
                                <button
                                    class="edit-link"
                                    onclick={() => (editUser = true)}
                                    >Edit</button
                                >
                            </div>
                        {/if}
                    </div>
                </div>

                <div class="setting-item read-only">
                    <div class="info">
                        <label for="email">Email Address</label>
                        <p class="value">{user?.email || "..."}</p>
                    </div>
                    <span class="lock-icon" title="Cannot be changed">🔒</span>
                </div>

                <div class="setting-item read-only">
                    <div class="info">
                        <label for="plan">Current Plan</label>
                        <p class="value badge-value">
                            {user?.plan || "Free"}
                        </p>
                    </div>
                    <span class="lock-icon" title="Managed via Billing">🔒</span
                    >
                </div>
            </div>

            <div class="card-footer">
                <p>Member ID: <span class="mono">{user?.id || "..."}</span></p>
            </div>
        </div>
    </div>
</div>

<style>
    :global(body) {
        background-color: #f8fafc;
        margin: 0;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
            Arial, sans-serif;
    }

    .profile-page {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        padding: 20px;
        box-sizing: border-box;
    }

    .content-wrapper {
        width: 100%;
        max-width: 480px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    /* --- Alert Banner Styling --- */
    .alert-banner {
        background: #fef2f2;
        border: 1px solid #fee2e2;
        border-radius: 12px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.1);
        color: #991b1b;
    }

    .alert-icon svg {
        width: 24px;
        height: 24px;
        color: #ef4444;
    }

    .alert-content {
        flex: 1;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .alert-content strong {
        display: block;
        color: #7f1d1d;
        margin-bottom: 2px;
    }

    .alert-content p {
        margin: 0;
        color: #991b1b;
    }

    .retry-btn {
        background: #ef4444;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        white-space: nowrap;
    }

    .retry-btn:hover {
        background: #dc2626;
    }

    /* --- Profile Card Styling --- */
    .profile-card {
        background: white;
        border-radius: 24px;
        box-shadow:
            0 20px 25px -5px rgba(0, 0, 0, 0.05),
            0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #f1f5f9;
        overflow: hidden;
    }

    .card-header {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        padding: 40px 32px 24px;
        text-align: center;
        border-bottom: 1px solid #f1f5f9;
    }

    .avatar-container {
        position: relative;
        width: 96px;
        height: 96px;
        margin: 0 auto 16px;
    }

    .avatar-container img {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .status-badge {
        position: absolute;
        bottom: 4px;
        right: 4px;
        width: 14px;
        height: 14px;
        background: #10b981;
        border: 2px solid white;
        border-radius: 50%;
    }

    .card-header h1 {
        font-size: 1.25rem;
        color: #0f172a;
        margin: 0 0 4px;
        font-weight: 700;
    }

    .card-header p {
        color: #64748b;
        font-size: 0.9rem;
        margin: 0;
    }

    /* --- Settings List --- */
    .settings-list {
        padding: 8px 0;
    }

    .setting-item {
        padding: 20px 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f1f5f9;
        transition: background 0.2s;
    }

    .setting-item:last-child {
        border-bottom: none;
    }

    .setting-item:hover:not(.read-only) {
        background-color: #fcfcfc;
    }

    .info {
        flex: 1;
    }

    .info.full-width {
        width: 100%;
    }

    .info label {
        display: block;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .display-value-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 28px; /* Fixed height to prevent jumping */
    }

    .value {
        font-size: 1rem;
        color: #334155;
        font-weight: 500;
        margin: 0;
    }

    .badge-value {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    /* --- Inputs and Edit Mode --- */
    .input-wrapper {
        display: flex;
        gap: 8px;
        align-items: center;
        width: 100%;
    }

    input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font-size: 0.95rem;
        color: #0f172a;
        outline: none;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .input-actions {
        display: flex;
        gap: 4px;
    }

    .btn-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.2s;
    }

    .btn-save {
        background: #3b82f6;
        color: white;
    }
    .btn-save:hover {
        background: #2563eb;
    }
    .btn-save:disabled {
        background: #93c5fd;
        cursor: not-allowed;
    }

    .btn-cancel {
        background: #f1f5f9;
        color: #64748b;
    }
    .btn-cancel:hover {
        background: #e2e8f0;
        color: #ef4444;
    }

    .edit-link {
        background: none;
        border: none;
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
    }

    .edit-link:hover {
        background: #eff6ff;
    }

    /* --- Read Only States --- */
    .read-only {
        background-color: #fafafa;
    }

    .lock-icon {
        font-size: 0.9rem;
        opacity: 0.3;
        user-select: none;
    }

    /* --- Footer --- */
    .card-footer {
        padding: 24px;
        text-align: center;
        background: #f8fafc;
        border-top: 1px solid #f1f5f9;
    }

    .card-footer p {
        color: #94a3b8;
        font-size: 0.8rem;
        margin: 0;
    }

    .mono {
        font-family: monospace;
        background: #e2e8f0;
        padding: 2px 6px;
        border-radius: 4px;
        color: #64748b;
    }

    /* Spinner animation */
    .spinner {
        width: 12px;
        height: 12px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>
