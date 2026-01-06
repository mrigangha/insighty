<script>
    import { location } from "svelte-spa-router";
    import {
        getLoggedIn,
        setLoggedIn,
        URL,
        getAccessToken,
        setAccessToken,
        logout,
    } from "../lib/store.svelte";

    let isOpen = $state(false);
    let isLoggedIn = $derived(getLoggedIn());
    $inspect(isLoggedIn);
    const navLinks = [
        { path: "/", label: "Home" },
        { path: "/products", label: "Products" },
        { path: "/about", label: "Developers" },
        { path: "/pricing", label: "Pricing" },
    ];

    const LoggedInSkills = [{ path: "/projects", label: "Projects" }];

    let width = $state(window.innerWidth);

    window.addEventListener("resize", () => {
        width = window.innerWidth;
    });

    $effect(() => {
        if (width > 800) {
            isOpen = false;
        }
    });
</script>

<nav class="navbar">
    <div class="container">
        <div class="nav-inner">
            <!-- Logo -->
            <div class="logo">
                <a href="/">SAAS</a>
            </div>

            <!-- Desktop Menu -->
            <div class="menu">
                {#if isLoggedIn}
                    {#each LoggedInSkills as { path, label }}
                        <a
                            href={"#" + path}
                            class:selected={$location === path}
                        >
                            {label}
                        </a>
                    {/each}
                {:else}
                    {#each navLinks as { path, label }}
                        <a
                            href={"#" + path}
                            class:selected={$location === path}
                        >
                            {label}
                        </a>
                    {/each}
                {/if}
            </div>

            <!-- CTA -->
            <div class="cta">
                {#if !isLoggedIn}
                    <a href="#/login" class="login">Login</a>
                    <a href="#/register" class="signup">Sign Up</a>
                {:else}
                    <a href="#/profile" class="profile">Profile</a>
                    <a
                        href="#/login"
                        class="logout"
                        onclick={async () => {
                            await logout();
                            setLoggedIn(false);
                        }}
                    >
                        Logout
                    </a>
                {/if}
            </div>

            <!-- Mobile Button -->
            <button
                class="mobile-btn"
                aria-label="Toggle navigation"
                aria-expanded={isOpen}
                onclick={() => (isOpen = !isOpen)}
            >
                <span class:open={isOpen}></span>
                <span class:open={isOpen}></span>
                <span class:open={isOpen}></span>
            </button>
        </div>
    </div>

    <!-- Mobile Menu -->
    {#if isOpen}
        <div class="mobile-menu">
            {#if isLoggedIn}
                {#each LoggedInSkills as { path, label }}
                    <a
                        href={"#" + path}
                        class:selected={$location === path}
                        onclick={() => (isOpen = false)}
                    >
                        {label}
                    </a>
                {/each}
                <a href="#/profile" onclick={() => (isOpen = false)}>
                    Profile
                </a>
                <a
                    href="#/login"
                    onclick={async () => {
                        await logout();
                        setLoggedIn(false);
                        isOpen = false;
                    }}
                >
                    Logout
                </a>
            {:else}
                {#each navLinks as { path, label }}
                    <a
                        href={"#" + path}
                        class:selected={$location === path}
                        onclick={() => (isOpen = false)}
                    >
                        {label}
                    </a>
                {/each}
                <a href="#/login" onclick={() => (isOpen = false)}>Login</a>
                <a href="#/register" onclick={() => (isOpen = false)}>
                    Sign Up
                </a>
            {/if}
        </div>
    {/if}
</nav>

<style>
    /* --- Navbar --- */
    .navbar {
        border-bottom: 1px solid #e5e7eb;
        background: white;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 16px;
    }

    .nav-inner {
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* --- Logo --- */
    .logo a {
        font-size: 24px;
        font-weight: 700;
        text-decoration: none;
        color: #4b4bff;
    }

    /* --- Desktop Menu --- */
    .menu {
        display: flex;
        gap: 24px;
    }

    .menu a {
        text-decoration: none;
        font-size: 16px;
        color: #334155;
        padding-bottom: 4px;
        transition: 0.2s;
    }

    .menu a:hover {
        color: #4b4bff;
    }

    .menu a.selected {
        color: #4b4bff;
        border-bottom: 2px solid #4b4bff;
    }

    /* --- CTA --- */
    .cta {
        display: flex;
        gap: 14px;
    }

    .login,
    .signup,
    .profile,
    .logout {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 15px;
        text-decoration: none;
        font-weight: 600;
        transition: 0.2s;
    }

    .login,
    .profile {
        border: 1px solid #4b4bff;
        color: #4b4bff;
        background: transparent;
    }

    .login:hover,
    .profile:hover {
        background: #eef2ff;
    }

    .signup {
        background: #4b4bff;
        color: white;
    }

    .signup:hover {
        background: #3b3bd6;
    }

    .logout {
        background: #fee2e2;
        color: #b91c1c;
    }

    /* --- Mobile Button --- */
    .mobile-btn {
        display: none;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    .mobile-btn span {
        display: block;
        width: 20px;
        height: 2px;
        background: #334155;
        border-radius: 2px;
        transition:
            transform 0.25s ease,
            opacity 0.2s ease;
    }

    .mobile-btn span:nth-child(1).open {
        transform: translateY(6px) rotate(45deg);
    }

    .mobile-btn span:nth-child(2).open {
        opacity: 0;
    }

    .mobile-btn span:nth-child(3).open {
        transform: translateY(-6px) rotate(-45deg);
    }

    /* --- Mobile Menu --- */
    .mobile-menu {
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        animation: slideDown 0.25s ease;
    }

    .mobile-menu a {
        display: block;
        padding: 10px 0;
        text-decoration: none;
        font-size: 16px;
        color: #334155;
    }

    .mobile-menu a.selected {
        color: #4b4bff;
        font-weight: 700;
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-6px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* --- Responsive --- */
    @media (max-width: 768px) {
        .menu,
        .cta {
            display: none;
        }

        .mobile-btn {
            display: flex;
        }
    }
</style>
