<script>
    import { getOpenProjectTrackingKey } from "../lib/store.svelte";
    let copied = $state(false);

    function copyToClipboard() {
        const value = getOpenProjectTrackingKey();
        if (!value) return;

        navigator.clipboard.writeText(value).then(() => {
            copied = true;
            setTimeout(() => (copied = false), 1500);
        });
    }
</script>

<div class="settings">
    <h2>Tracking Key</h2>

    <div class="copy-box">
        <code>{getOpenProjectTrackingKey()}</code>

        <button on:click={copyToClipboard}>
            {copied ? "Copied ✓" : "Copy"}
        </button>
    </div>
</div>
