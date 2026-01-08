<script>
    import { getOpenProjectTrackingKey } from "../lib/store.svelte";

    let copiedKey = $state(false);
    let copiedScript = $state(false);

    const trackingKey = $derived(getOpenProjectTrackingKey());

    // The script template that users need to paste
    const scriptTag = $derived(
        `<script \n  src="https://yourdomain.com/insighty.js" \n  data-tracking-key="${trackingKey}"\n><\/script>`,
    );

    function copyKey() {
        if (!trackingKey) return;
        navigator.clipboard.writeText(trackingKey).then(() => {
            copiedKey = true;
            setTimeout(() => (copiedKey = false), 1500);
        });
    }

    function copyScript() {
        if (!trackingKey) return;
        navigator.clipboard.writeText(scriptTag).then(() => {
            copiedScript = true;
            setTimeout(() => (copiedScript = false), 1500);
        });
    }
</script>

<div class="settings-container">
    <section class="settings-section">
        <h2>Installation</h2>
        <p class="description">
            Copy and paste this script into the <code class="head"
                >&lt;head&gt;</code
            > of your website to start tracking leads.
        </p>

        <div class="code-block">
            <pre><code>{scriptTag}</code></pre>
            <button
                class="copy-btn"
                onclick={copyScript}
                class:success={copiedScript}
            >
                {#if copiedScript}
                    <span>Copied ✓</span>
                {:else}
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><rect
                            x="9"
                            y="9"
                            width="13"
                            height="13"
                            rx="2"
                            ry="2"
                        /><path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                        /></svg
                    >
                    <span>Copy Script</span>
                {/if}
            </button>
        </div>
    </section>

    <section class="settings-section">
        <h3>Tracking Key</h3>
        <p class="description">
            Your unique identifier for manual API integrations.
        </p>
        <div class="key-box">
            <code>{trackingKey || "No key found"}</code>
            <button class="text-copy-btn" onclick={copyKey}>
                {copiedKey ? "Copied!" : "Copy Key"}
            </button>
        </div>
    </section>
</div>

<style>
    .settings-container {
        max-width: 800px;
        font-family: "Inter", system-ui, sans-serif;
        display: flex;
        flex-direction: column;
        gap: 2.5rem;
        padding: 1rem;
    }

    h2 {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: #1e293b;
    }
    h3 {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        color: #334155;
    }

    .description {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    /* Script Copy Box */
    .code-block {
        background: #0f172a;
        border-radius: 12px;
        padding: 1.25rem;
        position: relative;
        border: 1px solid #1e293b;
    }

    pre {
        margin: 0;
        overflow-x: auto;
    }

    code {
        font-family: "JetBrains Mono", "Fira Code", monospace;
        font-size: 0.85rem;
        color: #e2e8f0;
        line-height: 1.6;
    }

    code.head {
        font-family: "JetBrains Mono", "Fira Code", monospace;
        font-size: 0.85rem;
        color: black;
        line-height: 1.6;
    }

    .copy-btn {
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
    }

    .copy-btn:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .copy-btn.success {
        background: #10b981;
        border-color: #10b981;
    }

    /* Key Copy Box */
    .key-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        border-radius: 8px;
    }

    .key-box code {
        color: #475569;
        font-weight: 600;
    }

    .text-copy-btn {
        background: transparent;
        border: none;
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        padding: 4px 8px;
    }

    .text-copy-btn:hover {
        text-decoration: underline;
    }
</style>
