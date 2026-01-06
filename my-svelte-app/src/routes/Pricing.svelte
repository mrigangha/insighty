<script>
    import { getPlan, setPlan } from "../lib/store.svelte.js";
    import { push } from "svelte-spa-router";
    // Data configuration for easy updates
    const plans = [
        {
            name: "Free",
            price: "0",
            period: "/mo",
            features: [
                "Basic Access",
                "Community Support",
                "1 Project",
                "Read-only API",
            ],
            isPopular: false,
            buttonText: "Get Started",
            buttonStyle: "outline",
        },
        {
            name: "Basic",
            price: "900",
            period: "/mo",
            features: [
                "Standard Analytics",
                "Email Support",
                "10 Projects",
                "Full API Access",
                "Custom Domain",
            ],
            isPopular: true,
            buttonText: "Choose Basic",
            buttonStyle: "filled",
        },
        {
            name: "Premium",
            price: "2,900",
            period: "/mo",
            features: [
                "Advanced Analytics",
                "24/7 Priority Support",
                "Unlimited Projects",
                "White Labeling",
                "SSO Authentication",
            ],
            isPopular: false,
            buttonText: "Go Premium",
            buttonStyle: "outline",
        },
    ];
</script>

<div class="pricing-wrapper">
    <div class="header">
        <h1>Simple, Transparent Pricing</h1>
        <p>Choose the plan that fits your growth</p>
    </div>

    <div class="pricing-grid">
        {#each plans as plan}
            <div class="card {plan.isPopular ? 'popular' : ''}">
                {#if plan.isPopular}
                    <div class="badge">Most Popular</div>
                {/if}

                <h2>{plan.name}</h2>

                <div class="price-container">
                    <span class="currency">₹</span>
                    <span class="amount">{plan.price}</span>
                    <span class="period">{plan.period}</span>
                </div>

                <ul class="features">
                    {#each plan.features as feature}
                        <li>{feature}</li>
                    {/each}
                </ul>

                <button
                    class="btn {plan.buttonStyle === 'filled'
                        ? 'btn-filled'
                        : 'btn-outline'}"
                    onclick={(e) => {
                        setPlan(plan.name);
                        push("/register");
                    }}
                >
                    {plan.buttonText}
                </button>
            </div>
        {/each}
    </div>
</div>

<style>
    /* Variables for easy theming */
    :global(body) {
        margin: 0;
        background-color: white;
        font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
            Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    }

    .pricing-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 1rem;
        min-height: 100vh;
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }

    .header {
        text-align: center;
        margin-bottom: 3.5rem;
    }

    .header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
    }

    .header p {
        font-size: 1.125rem;
        color: #64748b;
    }

    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        max-width: 1100px;
        width: 100%;
        align-items: center; /* Vertically center items if they have different heights */
    }

    .card {
        background: white;
        border-radius: 1.5rem;
        padding: 2.5rem;
        position: relative;
        display: flex;
        flex-direction: column;
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .card:hover {
        transform: translateY(-8px);
        box-shadow:
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    /* Popular Card Styling */
    .card.popular {
        border: 2px solid #6366f1;
        transform: scale(1.05);
        z-index: 10;
        box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.15);
    }

    .card.popular:hover {
        transform: scale(1.05) translateY(-8px);
    }

    .badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: #6366f1;
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #64748b;
        margin: 0 0 1rem 0;
    }

    .price-container {
        display: flex;
        align-items: baseline;
        margin-bottom: 2rem;
        color: #0f172a;
    }

    .currency {
        font-size: 1.5rem;
        font-weight: 600;
        margin-right: 2px;
    }

    .amount {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
    }

    .period {
        color: #94a3b8;
        font-size: 1rem;
        margin-left: 4px;
    }

    .features {
        list-style: none;
        padding: 0;
        margin: 0 0 2.5rem 0;
        flex-grow: 1;
    }

    .features li {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        color: #334155;
    }

    /* Custom Checkmark */
    .features li::before {
        content: "";
        display: inline-block;
        width: 1.25rem;
        height: 1.25rem;
        margin-right: 0.75rem;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2310b981' stroke-width='3'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M4.5 12.75l6 6 9-13.5' /%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
    }

    .btn {
        width: 100%;
        padding: 1rem;
        border-radius: 0.75rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-filled {
        background-color: #6366f1;
        color: white;
        border: 2px solid #6366f1;
    }

    .btn-filled:hover {
        background-color: #4f46e5;
        border-color: #4f46e5;
    }

    .btn-outline {
        background-color: transparent;
        color: #6366f1;
        border: 2px solid #e2e8f0;
    }

    .btn-outline:hover {
        border-color: #6366f1;
        background-color: #f5f3ff;
    }

    /* Mobile Responsiveness for the Popular card scaling */
    @media (max-width: 768px) {
        .card.popular {
            transform: scale(1);
            border-width: 2px;
        }
        .card.popular:hover {
            transform: translateY(-8px);
        }
    }
</style>
