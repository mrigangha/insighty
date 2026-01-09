<script>
    import { push } from "svelte-spa-router";
    import {
        URL,
        setLoggedIn,
        setAccessToken,
        getPlan,
    } from "../lib/store.svelte";
    import { onMount } from "svelte";
    let success = $state(false);
    let pricing = $state("Free");
    let isLoading = $state(false);
    let access_token = $state("");
    let is_pay = $derived.by(() => {
        if (pricing == "Free") {
            return false;
        } else {
            return true;
        }
    });
    const pricingPlans = {
        Free: 0,
        Basic: 90000, // ₹900 in paise
        Premium: 290000, // ₹2900 in paise
    };
    onMount(() => {
        pricing = getPlan();
    });
    async function verifyPaymentAndRegister(paymentResponse, userData) {
        try {
            // Verify payment signature
            const verifyResponse = await fetch(`${URL}/verifypayment`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${access_token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    razorpay_order_id: paymentResponse.razorpay_order_id,
                    razorpay_payment_id: paymentResponse.razorpay_payment_id,
                    razorpay_signature: paymentResponse.razorpay_signature,
                }),
            });

            if (!verifyResponse.ok) {
                throw new Error("Payment verification failed");
            }
            console.log(paymentResponse.razorpay_payment_id);
            console.log(paymentResponse.razorpay_order_id);

            setLoggedIn(true);
            alert("Login successful");
            setAccessToken(access_token);
            push("/profile");
        } catch (error) {
            console.error("Error:", error);
            alert(
                "Payment successful but registration failed. Contact support with payment ID: " +
                    paymentResponse.razorpay_payment_id,
            );
        } finally {
            isLoading = false;
        }
    }
</script>

<svelte:head>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
</svelte:head>

<div class="container">
    <div class="card">
        <div class="header">
            <h1>Create Account</h1>
            <p>Join us today and get started</p>
        </div>

        <form
            class="form"
            onsubmit={async (e) => {
                e.preventDefault();
                isLoading = true;
                const fd = new FormData(e.target);
                const data = Object.fromEntries(fd.entries());

                try {
                    const res = await fetch(`${URL}/register`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(data),
                    });
                    const result = await res.json();

                    if (!res.ok) {
                        alert("Registration failed");
                    } else {
                        alert("Registration successful");
                        if (data.pricing === "Free") {
                            alert("You have been assigned a free plan");
                            push("/login");
                        } else {
                            try {
                                const res = await fetch(`${URL}/login`, {
                                    method: "POST",
                                    credentials: "include",
                                    headers: {
                                        "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify({
                                        email: data.email,
                                        password: data.password,
                                    }),
                                });
                                const d = await res.json();
                                access_token = d.access_token;
                                let order = {
                                    amount: pricingPlans[data.pricing],
                                    currency: "INR",
                                    plan: data.pricing,
                                };
                                const resp = await fetch(
                                    `${URL}/paymentorder`,
                                    {
                                        method: "POST",
                                        credentials: "include",
                                        headers: {
                                            Authorization: `Bearer ${d.access_token}`,
                                            "Content-Type": "application/json",
                                        },
                                        body: JSON.stringify(order),
                                    },
                                );
                                const info = await resp.json();
                                const options = {
                                    key: "rzp_test_RznNlAeuXL0d3K", // Your test key
                                    amount: order.amount,
                                    currency: order.currency,
                                    name: "Your Company Name",
                                    description: `${pricing} Plan Subscription`,
                                    order_id: info.order_id, // Use the order_id from response
                                    handler: async function (response) {
                                        // This runs after successful payment
                                        await verifyPaymentAndRegister(
                                            response,
                                            data,
                                        );
                                    },
                                    prefill: {
                                        name: data.name,
                                        email: data.email,
                                    },
                                    theme: {
                                        color: "#4f46e5",
                                    },
                                    modal: {
                                        ondismiss: function () {
                                            isLoading = false;
                                            alert("Payment cancelled");
                                        },
                                    },
                                };

                                const rzp = new window.Razorpay(options);
                                rzp.open(); // Th
                            } catch (error) {
                            } finally {
                                isLoading = false;
                            }
                        }
                    }
                } catch (error) {
                    alert("An error occurred. Please try again.");
                } finally {
                    isLoading = false;
                }
            }}
        >
            <div class="form-group">
                <label for="name">Full Name</label>
                <input
                    id="name"
                    type="text"
                    name="name"
                    placeholder="John Doe"
                    required
                />
            </div>

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

            <div class="form-group">
                <label for="pricing">Pricing Plan</label>
                <select id="pricing" name="pricing" bind:value={pricing}>
                    <option value="Free">Free - Get started at no cost</option>
                    <option value="Basic">Basic - Rs900/month</option>
                    <option value="Premium">Premium - Rs2900/month</option>
                </select>
            </div>

            <button class="submit-btn" type="submit" disabled={isLoading}>
                {#if is_pay}
                    {#if isLoading}
                        <span class="spinner"></span>
                        Processing your payment...
                    {:else}
                        Pay and Create Account
                    {/if}
                {:else if isLoading}
                    <span class="spinner"></span>
                    Creating Account...
                {:else}
                    Create Account
                {/if}
            </button>
        </form>

        <div class="footer">
            <p>Already have an account? <a href="#/login">Sign in</a></p>
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

    .form-group input,
    .form-group select {
        width: 100%;
        padding: 14px 16px;
        font-size: 16px;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        background: #f7fafc;
        transition: all 0.2s ease;
        color: #2d3748;
    }

    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: #4f46e5;
        background: white;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    .form-group input::placeholder {
        color: #a0aec0;
    }

    .form-group select {
        cursor: pointer;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%232d3748' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 16px center;
        padding-right: 40px;
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
