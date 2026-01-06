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
    onclick={() => {
        onProjectClick(project_id, project_name, project_trackingkey);
    }}
    class="project-card"
>
    <div class="project-card-header">
        <h3>{project_name}</h3>
        <div class="project-card-footer">
            <button
                onclick={async (e) => {
                    e.stopPropagation();
                    alert("Delete Project");
                    buttonClicked = true;
                    await onDeleteProject(project_id);
                }}>Delete</button
            >
        </div>
    </div>
    <div class="project-card-body">
        <p>{project_domain}</p>
    </div>
</div>

<style>
    .project-card {
        width: 300px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    .project-card:hover {
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }

    .project-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .project-card-body {
        margin-top: 10px;
    }

    .project-card-footer {
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
    }

    .project-card-footer button {
        padding: 5px 10px;
        border: none;
        border-radius: 5px;
        background-color: #ccc;
        color: #fff;
        cursor: pointer;
    }

    .project-card-footer button:hover {
        background-color: #999;
    }
</style>
