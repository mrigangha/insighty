<script>
    import ProjectCards from "./projects/ProjectCards.svelte";
    import { onMount } from "svelte";
    import {
        URL,
        setOpenProjectId,
        setOpenProjectName,
        setOpenProjectTrackingKey,
        getAccessToken,
    } from "../lib/store.svelte";
    import { push } from "svelte-spa-router";
    import { fade, scale } from "svelte/transition"; // Added for smoother feel

    let projects = $state([]);
    let createProject = $state(false);
    let newProjectName = $state("");
    let newProjectDomain = $state("");
    let isLoading = $state(true);

    function onOpenProject(projectId, projectName, projectTrackingKey) {
        setOpenProjectId(projectId);
        setOpenProjectName(projectName);
        setOpenProjectTrackingKey(projectTrackingKey);
        push("/leads");
    }

    async function onDeleteProject(projectId) {
        if (!confirm("Are you sure you want to delete this project?")) return;

        let token = getAccessToken();
        if (!token) return push("/login");

        const response = await fetch(`${URL}/project/${projectId}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
            await fetchProjects();
        }
    }

    async function createNewProject() {
        if (!newProjectName) return alert("Project name is required");

        let token = getAccessToken();
        if (!token) return push("/login");

        const response = await fetch(`${URL}/project`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                name: newProjectName,
                domain: newProjectDomain,
            }),
        });

        if (response.ok) {
            newProjectName = "";
            newProjectDomain = "";
            createProject = false;
            await fetchProjects();
        }
    }

    async function fetchProjects() {
        let token = getAccessToken();
        if (!token) return push("/login");

        try {
            const response = await fetch(`${URL}/projects`, {
                method: "GET",
                headers: { Authorization: `Bearer ${token}` },
            });
            const data = await response.json();
            projects = data["projects"] || [];
        } catch (e) {
            console.error("Failed to fetch", e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => fetchProjects());
</script>

<div class="projects-container">
    <header class="page-header">
        <div class="header-content">
            <h1>My Projects</h1>
            <p>Welcome back! Manage your tracking and insights below.</p>
        </div>
        <button class="btn-primary" onclick={() => (createProject = true)}>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><line x1="12" y1="5" x2="12" y2="19"></line><line
                    x1="5"
                    y1="12"
                    x2="19"
                    y2="12"
                ></line></svg
            >
            <span>New Project</span>
        </button>
    </header>

    {#if isLoading}
        <div class="loading-container" in:fade>
            <div class="spinner"></div>
            <p>Gathering your projects...</p>
        </div>
    {:else if projects.length === 0}
        <div class="empty-state" in:scale={{ duration: 400, start: 0.95 }}>
            <div class="empty-icon-wrapper">
                <div class="empty-icon">📁</div>
            </div>
            <h2>No projects found</h2>
            <p>
                Your workspace is empty. Create your first project to start
                tracking leads today.
            </p>
            <button class="btn-outline" onclick={() => (createProject = true)}>
                Get Started
            </button>
        </div>
    {:else}
        <div class="project-grid" in:fade>
            {#each projects as project}
                <ProjectCards
                    project_trackingkey={project.tracking_key}
                    project_name={project.name}
                    project_id={project.id}
                    project_domain={project.domain}
                    onProjectClick={onOpenProject}
                    {onDeleteProject}
                />
            {/each}
        </div>
    {/if}

    {#if createProject}
        <div class="modal-backdrop" in:fade={{ duration: 200 }}>
            <div class="modal" in:scale={{ duration: 250, start: 0.9 }}>
                <div class="modal-header">
                    <h3>Create New Project</h3>
                    <p>Set up a new workspace for your leads.</p>
                </div>

                <div class="modal-body">
                    <div class="form-group">
                        <label for="pname">Project Name</label>
                        <input
                            id="pname"
                            type="text"
                            placeholder="e.g. My Awesome SaaS"
                            bind:value={newProjectName}
                        />
                    </div>
                    <div class="form-group">
                        <label for="pdomain"
                            >Project Domain <span class="optional"
                                >(Optional)</span
                            ></label
                        >
                        <input
                            id="pdomain"
                            type="text"
                            placeholder="e.g. example.com"
                            bind:value={newProjectDomain}
                        />
                    </div>
                </div>

                <div class="modal-actions">
                    <button
                        class="btn-text"
                        onclick={() => (createProject = false)}
                    >
                        Cancel
                    </button>
                    <button class="btn-primary" onclick={createNewProject}>
                        Create Project
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    :global(body) {
        background-color: #f8fafc; /* Lighter, cleaner background */
    }

    .projects-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 60px 24px;
        min-height: 100vh;
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end; /* Aligns button with text baseline */
        margin-bottom: 48px;
    }

    .header-content h1 {
        margin: 0;
        font-size: 2.25rem;
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    .header-content p {
        margin: 8px 0 0 0;
        color: #64748b;
        font-size: 1.1rem;
    }

    /* Grid Layout */
    .project-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 32px;
    }

    /* Modal Styles */
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .modal {
        background: white;
        padding: 40px;
        border-radius: 24px;
        width: 100%;
        max-width: 480px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .modal-header h3 {
        margin: 0;
        font-size: 1.5rem;
        color: #0f172a;
        font-weight: 700;
    }

    .modal-header p {
        color: #64748b;
        margin: 4px 0 24px 0;
        font-size: 0.95rem;
    }

    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 8px;
        color: #334155;
    }

    .optional {
        color: #94a3b8;
        font-weight: 400;
        font-size: 0.8rem;
    }

    .form-group input {
        width: 100%;
        padding: 14px 16px;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.2s;
        background: #fdfdfd;
    }

    .form-group input:focus {
        outline: none;
        border-color: #3b82f6;
        background: white;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 16px;
        margin-top: 40px;
    }

    /* Buttons */
    .btn-primary {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        filter: brightness(1.05);
    }

    .btn-primary:active {
        transform: translateY(0);
    }

    .btn-outline {
        background: white;
        border: 1px solid #e2e8f0;
        color: #0f172a;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-outline:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
    }

    .btn-text {
        background: transparent;
        border: none;
        color: #64748b;
        font-weight: 600;
        cursor: pointer;
        padding: 8px 16px;
        border-radius: 8px;
        transition: all 0.2s;
    }

    .btn-text:hover {
        background: #f1f5f9;
        color: #0f172a;
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 80px 40px;
        background: white;
        border: 2px dashed #e2e8f0;
        border-radius: 32px;
        max-width: 600px;
        margin: 40px auto;
    }

    .empty-icon-wrapper {
        width: 80px;
        height: 80px;
        background: #f1f5f9;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px auto;
    }

    .empty-icon {
        font-size: 2.5rem;
    }

    .empty-state h2 {
        color: #0f172a;
        margin-bottom: 12px;
    }

    .empty-state p {
        color: #64748b;
        margin-bottom: 32px;
        line-height: 1.6;
    }

    /* Loading Spinner */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 120px 0;
        color: #64748b;
    }

    .spinner {
        width: 48px;
        height: 48px;
        border: 3px solid #e2e8f0;
        border-top: 3px solid #2563eb;
        border-radius: 50%;
        animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        margin-bottom: 20px;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    @media (max-width: 640px) {
        .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 20px;
        }

        .btn-primary {
            width: 100%;
            justify-content: center;
        }
    }
</style>
