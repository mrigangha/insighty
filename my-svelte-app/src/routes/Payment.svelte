<script>
    import { onMount } from "svelte";
    import { push } from "svelte-spa-router";
    import { fade, slide } from "svelte/transition";
    import {
        URL,
        getPlan,
        setPlan,
        getAccessToken,
        getLoggedInUser,
    } from "../lib/store.svelte.js";

    const pricingPlans = {
        Free: 0,
        Basic: 90000, // ₹900 in paise
        Premium: 290000, // ₹2900 in paise
    };

    let access_token;

    // UI States
    let status = $state("initializing"); // initializing | open | verifying | success | cancelled | error
    let errorMessage = $state("");

    async function verifyPaymentAndRegister(paymentResponse, userData) {
        status = "verifying"; // Update UI to show verification spinner

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

            status = "success";
            // Small delay to let user see the success checkmark before redirecting
            setTimeout(() => {
                push("/profile");
            }, 1500);
        } catch (error) {
            console.error("Error:", error);
            status = "error";
            errorMessage =
                "Payment successful but verification failed. Please contact support with ID: " +
                paymentResponse.razorpay_payment_id;
        }
    }

    onMount(async () => {
        try {
            access_token = getAccessToken();
            if (!access_token) {
                push("/profile");
                return;
            }

            let currentPlan = getPlan();

            // Generate Order
            let order = {
                amount: pricingPlans[currentPlan],
                currency: "INR",
                plan: currentPlan,
            };

            const resp = await fetch(`${URL}/paymentorder`, {
                method: "POST",
                credentials: "include",
                headers: {
                    Authorization: `Bearer ${access_token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(order),
            });

            if (!resp.ok) throw new Error("Could not initiate order");

            const info = await resp.json();

            const options = {
                key: "rzp_test_RznNlAeuXL0d3K",
                amount: order.amount,
                currency: order.currency,
                name: "Your Company Name",
                description: `${currentPlan} Plan Subscription`,
                order_id: info.order_id,
                handler: async function (response) {
                    await verifyPaymentAndRegister(response, getLoggedInUser());
                },
                prefill: getLoggedInUser(),
                theme: {
                    color: "#4f46e5",
                },
                modal: {
                    ondismiss: function () {
                        status = "cancelled"; // Update UI instead of Alert
                    },
                },
            };

            const rzp = new window.Razorpay(options);

            // Slight delay ensures the UI renders "Initializing" before the heavy modal pops
            setTimeout(() => {
                rzp.open();
                status = "open";
            }, 500);
        } catch (error) {
            console.error(error);
            status = "error";
            errorMessage =
                "Could not connect to payment gateway. Please try again.";
        }
    });

    function retryPayment() {
        window.location.reload();
    }

    function goBack() {
        push("/profile");
    }
</script>

<svelte:head>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
</svelte:head>

<div class="payment-container" in:fade>
    <div class="payment-card">
        {#if status === "initializing"}
            <div class="state-content">
                <div class="spinner"></div>
                <h2>Secure Checkout</h2>
                <p>Establishing secure connection to gateway...</p>
            </div>
        {:else if status === "open"}
            <div class="state-content dimmed">
                <div class="shield-icon">🛡️</div>
                <h2>Payment in Progress</h2>
                <p>Please complete the payment in the popup window.</p>
                <small>Do not close this tab.</small>
            </div>
        {:else if status === "verifying"}
            <div class="state-content" in:slide>
                <div class="spinner blue"></div>
                <h2>Verifying Transaction</h2>
                <p>Please wait while we confirm your payment...</p>
                <div class="warning-text">Do not refresh the page</div>
            </div>
        {:else if status === "success"}
            <div class="state-content success" in:slide>
                <div class="icon-circle check">✓</div>
                <h2>Payment Successful!</h2>
                <p>Redirecting you to your profile...</p>
            </div>
        {:else if status === "cancelled"}
            <div class="state-content error" in:slide>
                <div class="icon-circle cross">✕</div>
                <h2>Payment Cancelled</h2>
                <p>You cancelled the transaction before it was completed.</p>
                <div class="actions">
                    <button class="btn-primary" onclick={retryPayment}
                        >Try Again</button
                    >
                    <button class="btn-secondary" onclick={goBack}
                        >Return to Profile</button
                    >
                </div>
            </div>
        {:else if status === "error"}
            <div class="state-content error" in:slide>
                <div class="icon-circle warning">!</div>
                <h2>Transaction Failed</h2>
                <p>{errorMessage}</p>
                <div class="actions">
                    <button class="btn-primary" onclick={retryPayment}
                        >Retry</button
                    >
                    <button class="btn-secondary" onclick={goBack}
                        >Cancel</button
                    >
                </div>
            </div>
        {/if}

        <div class="footer-trust">
            <span>🔒 256-bit SSL Secure Payment</span>
        </div>
    </div>
</div>

<style>
    :global(body) {
        margin: 0;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
            Arial, sans-serif;
        background-color: #f3f4f6;
    }

    .payment-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        width: 100%;
        padding: 20px;
        box-sizing: border-box;
    }

    .payment-card {
        background: white;
        width: 100%;
        max-width: 420px;
        padding: 40px 30px;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .state-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        animation: fadeIn 0.5s ease;
    }

    .state-content.dimmed {
        opacity: 0.6;
        filter: grayscale(1);
    }

    h2 {
        margin: 0;
        color: #111827;
        font-size: 1.5rem;
    }

    p {
        margin: 0;
        color: #6b7280;
        line-height: 1.5;
    }

    small {
        color: #9ca3af;
        font-size: 0.85rem;
    }

    .warning-text {
        color: #d97706;
        font-weight: 500;
        font-size: 0.9rem;
        background: #fffbeb;
        padding: 8px 16px;
        border-radius: 20px;
    }

    /* --- Icons --- */
    .shield-icon {
        font-size: 3rem;
        margin-bottom: 10px;
    }

    .icon-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: white;
        margin-bottom: 10px;
    }

    .icon-circle.check {
        background: #10b981;
    }
    .icon-circle.cross {
        background: #ef4444;
    }
    .icon-circle.warning {
        background: #f59e0b;
    }

    /* --- Spinner --- */
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #e5e7eb;
        border-top-color: #4f46e5;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
    }

    .spinner.blue {
        border-top-color: #3b82f6;
        border-left-color: #3b82f6;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* --- Buttons --- */
    .actions {
        display: flex;
        gap: 12px;
        margin-top: 10px;
        width: 100%;
    }

    button {
        flex: 1;
        padding: 12px;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.1s;
    }

    button:active {
        transform: scale(0.98);
    }

    .btn-primary {
        background: #4f46e5;
        color: white;
    }

    .btn-secondary {
        background: #f3f4f6;
        color: #4b5563;
    }

    /* --- Footer --- */
    .footer-trust {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #f3f4f6;
        color: #9ca3af;
        font-size: 0.8rem;
        display: flex;
        justify-content: center;
        gap: 8px;
    }
</style>
