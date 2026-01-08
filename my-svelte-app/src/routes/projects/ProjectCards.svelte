<script>
    let {
        project_trackingkey,
        project_name,
        project_id,
        project_domain,
        onDeleteProject,
        onProjectClick,
    } = $props();

    let buttonClicked = $state(false);
</script>

<div
    onclick={() =>
        onProjectClick(project_id, project_name, project_trackingkey)}
    class="project-card"
>
    <div class="project-card-header">
        <h3>{project_name}</h3>
        <button
            class="delete-btn"
            title="Delete Project"
            onclick={async (e) => {
                e.stopPropagation();
                if (confirm("Are you sure you want to delete this project?")) {
                    buttonClicked = true;
                    await onDeleteProject(project_id);
                }
            }}
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path d="M3 6h18" /><path
                    d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"
                /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /></svg
            >
        </button>
    </div>

    <div class="project-card-body">
        <p class="domain-text">{project_domain}</p>
    </div>

    <div class="project-card-footer">
        <span class="key-label">Tracking Key</span>
        <code class="key-value">{project_trackingkey}</code>
    </div>
</div>

<style>
    /* Scoped variables */
    :root {
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --accent-red: #ef4444;
        --bg-subtle: #f8fafc;
        --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        --shadow-hover: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }

    .project-card {
        width: 300px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-sm);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 160px; /* Gives consistent height */
    }

    .project-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: #cbd5e1;
    }

    /* Header: Name and Delete Button */
    .project-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-main);
        line-height: 1.2;
        padding-right: 10px; /* Space for delete button */
    }

    .delete-btn {
        flex-shrink: 0;
        padding: 6px;
        border: none;
        background: transparent;
        color: #94a3b8;
        border-radius: 6px;
        cursor: pointer;
        transition:
            color 0.2s,
            background-color 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .delete-btn:hover {
        background-color: #fee2e2;
        color: var(--accent-red);
    }

    /* Body: Domain */
    .project-card-body {
        flex-grow: 1; /* Pushes footer down */
        margin-bottom: 20px;
    }

    .domain-text {
        margin: 0;
        font-size: 0.95rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Footer: Tracking Key */
    .project-card-footer {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding-top: 12px;
        border-top: 1px dashed #e2e8f0;
    }

    .key-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 600;
    }

    .key-value {
        font-family:
            "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 0.85rem;
        color: #334155;
        background: var(--bg-subtle);
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid #f1f5f9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
