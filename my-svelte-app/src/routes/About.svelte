<script>
</script>

<div class="page-wrapper">
    <div class="content">
        <p class="name">Mrigangha Gupta</p>

        <p class="description">
            Software engineer helping businesses automate workflows and build
            reliable, scalable systems.
        </p>

        <p class="stack">Svelte · FastAPI · PostgreSQL</p>

        <p class="contact">
            <a href="mailto:guptamrigangha@email.com"
                >guptamrigangha@email.com</a
            >
        </p>
    </div>
</div>

<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

    /* Same background & horizontal rhythm as home page */
    .page-wrapper {
        min-height: 100vh;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }

    /* Match home page left padding (2rem) and centered width */
    .content {
        max-width: 900px;
        margin: 0 auto;
        padding: 1.5rem 2rem 3rem 2rem; /* same left/right as home */
        font-family:
            Inter,
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .name {
        font-size: 1.7rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #020617;
        margin-bottom: 1.2rem;
    }

    .description {
        font-size: 1.05rem;
        line-height: 1.75;
        color: #334155;
        margin-bottom: 1.1rem;
        max-width: 620px;
    }

    .stack {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.9rem;
        color: #475569;
        letter-spacing: 0.02em;
        margin-bottom: 1.4rem;
    }

    .contact a {
        font-size: 0.95rem;
        color: #4f46e5;
        text-decoration: none;
    }

    .contact a:hover {
        text-decoration: underline;
    }
</style>
