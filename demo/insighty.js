(function () {
  // Prevent double-loading
  if (window.__INSIGHTY__) return;
  window.__INSIGHTY__ = true;

  // Read tracking key from script tag
  const script = document.currentScript;
  const TRACKING_KEY = script?.dataset.trackingKey;

  if (!TRACKING_KEY) {
    console.warn("Insighty: tracking key missing");
    return;
  }

  const API_URL = "http://127.0.0.1:8000/";
  const SESSION_KEY = "insighty_session_id";

  /* ─────────────────────────────
     Session handling
  ───────────────────────────── */
  function getSessionId() {
    let id = localStorage.getItem(SESSION_KEY);
    //if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
    //}
    return id;
  }

  const sessionId = getSessionId();
  const response = fetch(API_URL + "sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    keepalive: true,
    body: JSON.stringify({
      session_id: sessionId,
      tracking_key: TRACKING_KEY,
    }),
  }).catch(() => {});
  response.then((res) => {
    if (res.ok) {
      res.json().then((data) => {
        console.log(data);
      });
    }
  });

  /* ─────────────────────────────
     Helpers
  ───────────────────────────── */
  function getCurrentPath() {
    // Hash routing
    if (location.hash && location.hash !== "#") {
      return location.hash.replace(/^#/, "");
    }
    // History routing (normal SPA)
    return location.pathname + location.search;
  }

  let lastPage = null;

  /* ─────────────────────────────
     Send event
  ───────────────────────────── */
  function sendEvent(type, data = {}) {
    let value = 0;
    if (type === "scroll") {
      value = data.percent;
    }
    const payload = {
      session_id: localStorage.getItem(SESSION_KEY),
      event_type: type,
      path: getCurrentPath(),
      tracking_key: TRACKING_KEY,
      value: value,
    };

    // Avoid duplicate page views
    if (type === "page_view") {
      if (payload.path === lastPage) return;
      lastPage = payload.path;
    }
    if (type === "click") {
      payload.click_target = data.meta.text;
      console.log(payload.click_target);
    }

    fetch(API_URL + "events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      keepalive: true,
      body: JSON.stringify(payload),
    })
      .catch(() => {})
      .then(() => {
        console.log("Event sent successfully");
      });
  }
  const SCROLL_THRESHOLDS = [25, 50, 75, 100];
  let firedScrolls = new Set();
  let scrollTimeout = null;
  /* ─────────────────────────────
     Hash routing support
  ───────────────────────────── */
  window.addEventListener("hashchange", () => {
    firedScrolls.clear();
    sendEvent("page_view");
  });

  /* ─────────────────────────────
     History API routing support
  ───────────────────────────── */
  ["pushState", "replaceState"].forEach((method) => {
    const original = history[method];
    history[method] = function (...args) {
      const result = original.apply(this, args);
      sendEvent("page_view");
      return result;
    };
  });

  window.addEventListener("popstate", () => {
    sendEvent("page_view");
  });

  function getScrollPercent() {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;

    if (docHeight <= 0) return 100;
    return Math.round((scrollTop / docHeight) * 100);
  }

  document.addEventListener("click", (e) => {
    const el = e.target.closest("a, button, input, [role='button']");
    if (!el) return;

    const text = (el.innerText || el.value || "").trim().slice(0, 100);

    const payload = {
      element: el.tagName.toLowerCase(),
      text,
      href: el.getAttribute("href") || null,
      id: el.id || null,
      classes: el.className
        ? el.className.toString().split(" ").slice(0, 3)
        : [],
    };

    sendEvent("click", {
      meta: payload,
    });
  });

  window.addEventListener("scroll", () => {
    // Throttle (runs after scrolling stops)
    if (scrollTimeout) return;

    scrollTimeout = setTimeout(() => {
      scrollTimeout = null;

      const percent = getScrollPercent();

      sendEvent("scroll", {
        percent: percent,
      });
    }, 300);
  });

  /* ─────────────────────────────
     Public API
  ───────────────────────────── */
  window.insighty = {
    track(event, data = {}) {
      sendEvent(event, data);
    },
    identify(leadId) {
      sendEvent("identify", { lead_id: leadId });
    },
  };
})();
