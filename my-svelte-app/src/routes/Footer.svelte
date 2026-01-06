<script>
    import { location } from "svelte-spa-router";

    const navLinks = [
        { path: "/", label: "Home" },
        { path: "/products", label: "Products" },
        { path: "/developers", label: "Developers" },
        { path: "/pricing", label: "Pricing" },
    ];
</script>

<div class="footer">
    <div class="lgo">
        <h1>@SAAS 2025</h1>
    </div>

    <div class="foot-menu">
        <h1>Links</h1>

        {#each navLinks as { path, label }}
            <a
                href={"#" + path}
                class:selected={$location === path}
            >
                {label}
            </a>
        {/each}
    </div>   
</div>

<style>
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 10px 20px;
    height: auto;              /* Better for responsiveness */
    border-top: 1px solid #eee;
    bottom: 0;
    left: 0;
    right: 0;
}

.lgo h1 {
    color: black;
    margin: 0;
    font-size: 16px;
    font-weight: 300;
    font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', sans-serif;
}

.foot-menu {
    display: flex;
    flex-direction: column;
    gap: 5px;
    text-align: right;
}

.foot-menu h1 {
    margin: 0;
    font-weight: 600;
    font-size: 16px;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, sans-serif;
}

.foot-menu a {
    text-decoration: none;
    color: black;
    font-size: 14px;
    transition: color 0.2s ease;
}

/* Avoid layout shift by not changing font-size on hover */
.foot-menu a:hover {
    color: #4b4bff;
}

.selected {
    font-weight: bold;
    color: #4b4bff;
}
</style>
