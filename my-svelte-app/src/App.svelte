<script>
    import Router, { location } from "svelte-spa-router"; // Added location import
    import Home from "./routes/Home.svelte";
    import About from "./routes/About.svelte";
    import Nav from "./routes/Nav.svelte";
    import Login from "./routes/Login.svelte";
    import Register from "./routes/Register.svelte";
    import Profile from "./routes/Profile.svelte";
    import { onMount } from "svelte";
    import {
        getLoggedIn,
        setLoggedIn,
        URL,
        getAccessToken,
        setAccessToken,
    } from "./lib/store.svelte";
    import Leads from "./routes/Leads.svelte";
    import Project from "./routes/Project.svelte";
    import Pricing from "./routes/Pricing.svelte";

    const routes = {
        "/": Home,
        "/about": About,
        "/login": Login,
        "/register": Register,
        "/profile": Profile,
        "/leads": Leads,
        "/projects": Project,
        "/pricing": Pricing,
    };

    // Define pages where the footer SHOULD be visible
    const publicPages = ["/", "/about", "/login", "/register"];

    onMount(async () => {
        let token = getAccessToken();
        if (!token) {
            const res = await fetch(`${URL}/refresh`, {
                credentials: "include",
                headers: { "Content-Type": "application/json" },
            });
            if (res.ok) {
                const data = await res.json();
                setAccessToken(data.access_token);
                token = getAccessToken();
            } else {
                return;
            }
        }
        const response = await fetch(`${URL}/me`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        });
        if (response.ok) {
            setLoggedIn(true);
        }
    });
</script>

<div class="app-wrapper">
    <Nav />

    <main class="content">
        <Router {routes} />
    </main>

    {#if publicPages.includes($location)}
        <footer>
            <div class="footer-container">
                <div class="footer-grid">
                    <div class="footer-brand">
                        <h3>App Name</h3>
                        <p>
                            Streamlining your workflow and managing your
                            projects with precision and ease.
                        </p>
                    </div>

                    <div class="footer-links">
                        <h4>Navigation</h4>
                        <ul>
                            <li><a href="#/">Home</a></li>
                            <li><a href="#/about">About</a></li>
                            <li><a href="#/login">Login</a></li>
                        </ul>
                    </div>

                    <div class="footer-contact">
                        <h4>Legal</h4>
                        <p>Privacy Policy</p>
                        <p>Terms of Service</p>
                    </div>
                </div>

                <div class="footer-bottom">
                    <p>
                        &copy; {new Date().getFullYear()} Your Company Name. All rights
                        reserved.
                    </p>
                </div>
            </div>
        </footer>
    {/if}
</div>

<style>
    /* GLOBAL RESET & SETTINGS
      This ensures your app looks consistent across all browsers
    */
    :global(*),
    :global(*::before),
    :global(*::after) {
        box-sizing: border-box;
    }

    :global(body, html) {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        font-family:
            "Inter",
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Oxygen,
            Ubuntu,
            Cantarell,
            "Open Sans",
            "Helvetica Neue",
            sans-serif;
        background-color: #f3f4f6; /* Light gray background to make white cards pop */
        color: #1f2937; /* Dark gray text for better readability than pure black */
        line-height: 1.5;
        -webkit-font-smoothing: antialiased; /* Makes fonts look sharper */
        -moz-osx-font-smoothing: grayscale;
    }

    :global(h1, h2, h3, h4, h5, h6) {
        line-height: 1.2;
        margin-bottom: 0.5em;
    }

    :global(a) {
        text-decoration: none;
        color: inherit;
    }

    /* APP LAYOUT */
    .app-wrapper {
        display: flex;
        flex-direction: column;
        min-height: 100vh; /* Forces footer to bottom if content is short */
    }

    .content {
        flex: 1; /* Takes up remaining space */
        width: 100%;
        position: relative;
    }

    /* FOOTER STYLES */
    footer {
        background-color: #111827; /* Dark Slate */
        color: #9ca3af; /* Muted gray text */
        padding: 4rem 0 2rem 0;
        border-top: 1px solid #1f2937;
        margin-top: auto; /* Double check to push footer down */
    }

    .footer-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }

    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 4rem;
        margin-bottom: 3rem;
    }

    .footer-brand h3 {
        color: #ffffff;
        margin: 0 0 1rem 0;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    .footer-brand p {
        font-size: 0.95rem;
        line-height: 1.6;
        max-width: 300px;
    }

    .footer-links h4,
    .footer-contact h4 {
        color: #f9fafb;
        margin-bottom: 1.25rem;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .footer-links ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .footer-links a {
        display: block;
        margin-bottom: 0.75rem;
        transition: color 0.2s ease;
        font-size: 0.95rem;
    }

    .footer-links a:hover {
        color: #6366f1; /* Indigo-500 hover state */
    }

    .footer-contact p {
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        cursor: pointer;
        transition: color 0.2s;
    }

    .footer-contact p:hover {
        color: #6366f1;
    }

    .footer-bottom {
        padding-top: 2rem;
        border-top: 1px solid #1f2937;
        text-align: center;
        font-size: 0.875rem;
        color: #6b7280;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .footer-grid {
            grid-template-columns: 1fr;
            gap: 2.5rem;
            text-align: center;
        }

        .footer-brand p {
            margin: 0 auto;
        }
    }
</style>
