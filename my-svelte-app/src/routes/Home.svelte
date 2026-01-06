<script>
    import { push } from "svelte-spa-router";
    import dashboard from "../assets/uidashboard.png";

    const openDemo = () => {
        push("/pricing");
    };
</script>

<div class="page-wrapper">
    <section class="hero">
        <div class="content">
            <div class="badge">AI-Powered Sales Intelligence</div>
            <h1>
                Understand Your Leads Before You Call <br />
                <span class="gradient-text">With AI Insights</span>
            </h1>

            <p>
                Stop guessing and start closing. See which leads are most likely
                to convert, identify hidden interests, and track performance
                with real-time analytics built specifically for high-performance
                sales teams.
            </p>

            <div class="buttons">
                <button class="primary" onclick={openDemo}>
                    View Live Demo
                    <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><path d="M5 12h14M12 5l7 7-7 7" /></svg
                    >
                </button>
                <button class="secondary" onclick={openDemo}>
                    Start Free Trial
                </button>
            </div>

            <div class="trust-row">
                <span class="item"
                    ><span class="check">✓</span> No credit card required</span
                >
                <span class="item"
                    ><span class="check">✓</span> Free 14-day trial</span
                >
                <span class="item"
                    ><span class="check">✓</span> Instant setup</span
                >
            </div>
        </div>

        <div class="image-box">
            <div class="image-container">
                <img src={dashboard} alt="Lead Insights Dashboard" />
            </div>
        </div>
    </section>
</div>

<style>
    .page-wrapper {
        background-color: #ffffff; /* Clean white background */
        min-height: calc(100vh - 80px); /* Adjust based on your nav height */
        display: flex;
        align-items: center;
    }

    .hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4rem 2rem;
        max-width: 1200px;
        margin: auto;
        gap: 5rem;
    }

    .content {
        flex: 1.2;
    }

    .badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        background: #f5f3ff;
        color: #4f46e5;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid #ddd6fe;
    }

    .hero h1 {
        font-size: 3.5rem;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.02em;
    }

    .gradient-text {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        font-size: 1.2rem;
        line-height: 1.6;
        color: #4b5563;
        margin-bottom: 2.5rem;
        max-width: 540px;
    }

    .buttons {
        display: flex;
        gap: 1rem;
        margin-bottom: 2.5rem;
    }

    .primary {
        background: #4f46e5;
        color: white;
        padding: 0.9rem 1.8rem;
        border-radius: 8px;
        font-size: 1rem;
        border: none;
        cursor: pointer;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition:
            background 0.2s,
            transform 0.1s;
    }

    .primary:hover {
        background: #4338ca;
    }

    .primary:active {
        transform: scale(0.98);
    }

    .secondary {
        padding: 0.9rem 1.8rem;
        border-radius: 8px;
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
        cursor: pointer;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s;
    }

    .secondary:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }

    .trust-row {
        font-size: 0.9rem;
        color: #6b7280;
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
    }

    .check {
        color: #10b981;
        font-weight: bold;
        margin-right: 0.25rem;
    }

    /* Dashboard Image Styling */
    .image-box {
        flex: 1;
        display: flex;
        justify-content: center;
    }

    .image-container {
        position: relative;
        padding: 8px;
        background: #f3f4f6;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow:
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    .image-container img {
        display: block;
        width: 100%;
        height: auto;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        /* No animation as requested */
    }

    @media (max-width: 1024px) {
        .hero h1 {
            font-size: 2.8rem;
        }
        .hero {
            gap: 2rem;
        }
    }

    @media (max-width: 900px) {
        .hero {
            flex-direction: column;
            text-align: center;
            padding: 4rem 1.5rem;
        }

        .hero p {
            margin: 0 auto 2.5rem auto;
        }

        .buttons {
            justify-content: center;
        }

        .trust-row {
            justify-content: center;
        }

        .image-box {
            width: 100%;
        }
    }
</style>
