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
    } from "../lib/store.svelte";
    import defaultAvatar from "../assets/default.png";
    import { fade, fly } from "svelte/transition";
    import { set } from "date-fns";

    let user = $state({ name: "", email: "", plan: "Free" });
    let editUser = $state(false);
    let nameValue = $state("");

    let isSaving = $state(false);

    async function checkAuth() {
        let token = getAccessToken();
        if (!token) {
            let location = localStorage.getItem("location");
            const status = await refreshAccessToken();
            if (!status) {
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
            console.log("here");
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
                <div class="info">
                    <label for="name">Full Name</label>
                    {#if editUser}
                        <div
                            class="input-wrapper"
                            in:fly={{ y: -10, duration: 200 }}
                        >
                            <input
                                id="name"
                                bind:value={nameValue}
                                onkeydown={(e) =>
                                    e.key === "Enter" && updateUser()}
                                autofocus
                            />
                            <div class="input-actions">
                                <button
                                    class="btn-save"
                                    onclick={updateUser}
                                    disabled={isSaving}
                                >
                                    {isSaving ? "..." : "Save"}
                                </button>
                                <button
                                    class="btn-cancel"
                                    onclick={() => (editUser = false)}>✕</button
                                >
                            </div>
                        </div>
                    {:else}
                        <p class="value">{user?.name || "Loading..."}</p>
                    {/if}
                </div>
                {#if !editUser}
                    <button
                        class="edit-toggle"
                        onclick={() => (editUser = true)}>Edit</button
                    >
                {/if}
            </div>

            <div class="setting-item read-only">
                <div class="info">
                    <label for="email">Email Address</label>
                    <p class="value">{user?.email}</p>
                </div>
                <span class="lock-icon">🔒</span>
            </div>

            <div class="setting-item read-only">
                <div class="info">
                    <label for="email">Plan</label>
                    <p class="value">{user?.plan}</p>
                </div>
                <span class="lock-icon">🔒</span>
            </div>
        </div>

        <div class="card-footer">
            <p>Member since 2024 • ID: {user?.id || "..."}</p>
        </div>
    </div>
</div>

<style>
    .profile-page {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        padding: 20px;
    }

    .profile-card {
        background: white;
        width: 100%;
        max-width: 500px;
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        overflow: hidden;
    }

    .card-header {
        background: linear-gradient(to bottom, #f8fafc, white);
        padding: 40px 32px 24px;
        text-align: center;
        border-bottom: 1px solid #f1f5f9;
    }

    .avatar-container {
        position: relative;
        width: 100px;
        height: 100px;
        margin: 0 auto 20px;
    }

    .avatar-container img {
        width: 100%;
        height: 100%;
        border-radius: 35%; /* Squircle look */
        object-fit: cover;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border: 4px solid white;
    }

    .status-badge {
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 16px;
        height: 16px;
        background: #10b981;
        border: 3px solid white;
        border-radius: 50%;
    }

    .card-header h1 {
        font-size: 1.5rem;
        color: #0f172a;
        margin: 0;
        font-weight: 800;
    }

    .card-header p {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 4px;
    }

    .settings-list {
        padding: 12px 32px;
    }

    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px 0;
        border-bottom: 1px solid #f1f5f9;
    }

    .setting-item:last-child {
        border-bottom: none;
    }

    .info label {
        display: block;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .info .value {
        font-size: 1.05rem;
        color: #1e293b;
        font-weight: 500;
        margin: 0;
    }

    /* Input Styling */
    .input-wrapper {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    input {
        padding: 8px 12px;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        font-size: 1rem;
        outline: none;
        width: 100%;
    }

    .btn-save {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
    }

    .btn-cancel {
        background: #f1f5f9;
        border: none;
        padding: 8px;
        border-radius: 6px;
        cursor: pointer;
    }

    .edit-toggle {
        background: transparent;
        border: 1px solid #e2e8f0;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s;
    }

    .edit-toggle:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
        color: #0f172a;
    }

    .read-only {
        opacity: 0.7;
    }

    .lock-icon {
        font-size: 1rem;
        filter: grayscale(1);
    }

    .card-footer {
        padding: 24px;
        text-align: center;
        background: #f8fafc;
        color: #94a3b8;
        font-size: 0.8rem;
    }
</style>
