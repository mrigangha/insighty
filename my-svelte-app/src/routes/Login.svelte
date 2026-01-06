<script>
    import { push } from "svelte-spa-router";
    let foot = $state(true);
    let err = $state(false);
    let isLoading = $state(false);
    import {
        getLoggedIn,
        setLoggedIn,
        setAccessToken,
    } from "../lib/store.svelte";
    import { URL } from "../lib/store.svelte";
    import { onMount } from "svelte";
    onMount(() => {
        if (getLoggedIn()) {
            push("/profile");
            return;
        }
        let token = localStorage.getItem("token");
        if (token && getLoggedIn()) {
            setLoggedIn(true);
            push("/profile");
            return;
        }
        err = false;
    });
</script>

<div class="container">
    <div class="card">
        <div class="header">
            <h1>Welcome Back</h1>
            <p>Sign in to your account to continue</p>
        </div>

        <form
            class="form"
            onsubmit={async (e) => {
                e.preventDefault();
                isLoading = true;
                const fd = new FormData(e.target);
                const data = Object.fromEntries(fd.entries());
                console.log(data);

                try {
                    const res = await fetch(`${URL}/login`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(data),
                    });
                    console.log(res.status);

                    if (!res.ok) {
                        err = true;
                        alert("Login failed");
                        return;
                    }

                    const result = await res.json();
                    setLoggedIn(true);
                    alert("Login successful");
                    setAccessToken(result.access_token);
                    push("/profile");
                } catch (error) {
                    err = true;
                    alert("An error occurred. Please try again.");
                } finally {
                    isLoading = false;
                }
            }}
        >
            <div class="form-group">
                <label for="email">Email Address</label>
                <input
                    id="email"
                    type="email"
                    name="email"
                    placeholder="you@example.com"
                    required
                />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    id="password"
                    type="password"
                    name="password"
                    placeholder="••••••••"
                    required
                />
            </div>

            {#if err}
                <div class="error-message">
                    Invalid email or password. Please try again.
                </div>
            {/if}

            <button class="submit-btn" type="submit" disabled={isLoading}>
                {#if isLoading}
                    <span class="spinner"></span>
                    Signing In...
                {:else}
                    Sign In
                {/if}
            </button>
        </form>

        <div class="footer">
            <p>Don't have an account? <a href="#/register">Sign up</a></p>
        </div>
    </div>
</div>

<style>
    * {
        box-sizing: border-box;
    }

    .container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        padding: 20px;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
            Ubuntu, Cantarell, sans-serif;
    }

    .card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        width: 100%;
        max-width: 480px;
        padding: 48px 40px;
        animation: slideUp 0.4s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .header {
        text-align: center;
        margin-bottom: 40px;
    }

    .header h1 {
        font-size: 32px;
        font-weight: 700;
        color: #1a202c;
        margin: 0 0 8px 0;
    }

    .header p {
        font-size: 16px;
        color: #718096;
        margin: 0;
    }

    .form {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .form-group label {
        font-size: 14px;
        font-weight: 600;
        color: #2d3748;
        letter-spacing: 0.3px;
    }

    .form-group input {
        width: 100%;
        padding: 14px 16px;
        font-size: 16px;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        background: #f7fafc;
        transition: all 0.2s ease;
        color: #2d3748;
    }

    .form-group input:focus {
        outline: none;
        border-color: #4f46e5;
        background: white;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    .form-group input::placeholder {
        color: #a0aec0;
    }

    .error-message {
        background: #fff5f5;
        border: 1px solid #fc8181;
        color: #c53030;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        text-align: center;
        animation: shake 0.4s ease-in-out;
    }

    @keyframes shake {
        0%,
        100% {
            transform: translateX(0);
        }
        25% {
            transform: translateX(-10px);
        }
        75% {
            transform: translateX(10px);
        }
    }

    .submit-btn {
        width: 100%;
        background: #4f46e5;
        color: white;
        padding: 16px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .submit-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
        background: #4338ca;
    }

    .submit-btn:active:not(:disabled) {
        transform: translateY(0);
    }

    .submit-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .footer {
        margin-top: 32px;
        text-align: center;
    }

    .footer p {
        font-size: 14px;
        color: #718096;
        margin: 0;
    }

    .footer a {
        color: #4f46e5;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s ease;
    }

    .footer a:hover {
        color: #4338ca;
        text-decoration: underline;
    }

    @media (max-width: 640px) {
        .card {
            padding: 32px 24px;
        }

        .header h1 {
            font-size: 28px;
        }

        .header p {
            font-size: 14px;
        }
    }
</style>
