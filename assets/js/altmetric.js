/* Keep a neutral empty ring until a real, positive official badge has loaded. */
(() => {
  const badges = [...document.querySelectorAll(".altmetric-embed")];
  if (!badges.length) return;
  const pending = [];
  badges.forEach((badge) => {
    const container = badge.closest(".attention");
    const fallback = container.querySelector(".attention-fallback");
    let currentImage;
    const state = (name) => {
      container.dataset.state = name;
      fallback.hidden = name === "available";
      const label = container.dataset[name === "empty" ? "empty" : name === "loading" ? "loading" : "unavailable"];
      fallback.setAttribute("aria-label", label);
      fallback.title = label;
    };
    const update = () => {
      // The official <1 filter hides zero or untracked records; never manufacture a score.
      if (badge.style.display === "none") state("empty");
      const image = badge.querySelector("img");
      if (!image) return;
      const reveal = () => {
        if (image.naturalWidth && badge.style.display !== "none") {
          state("available");
          watch.disconnect();
        }
      };
      // A vendor can reveal an already-loaded image after its first mutation.
      if (image === currentImage) { if (image.complete) reveal(); return; }
      currentImage = image;
      image.addEventListener("load", reveal, { once: true });
      image.addEventListener("error", () => { state("unavailable"); watch.disconnect(); }, { once: true });
      if (image.complete) reveal();
    };
    const watch = new MutationObserver(update);
    watch.observe(badge, { childList: true, subtree: true, attributes: true, attributeFilter: ["style"] });
    state("loading");
    pending.push({ watch, state, container });
  });
  let loading;
  const load = () => {
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://embed.altmetric.com/assets/embed.js";
      script.onload = resolve;
      script.onerror = reject;
      document.head.append(script);
    }).then(() => window._altmetric_embed_init?.()).catch(() => {
      pending.forEach(({ watch, state }) => { watch.disconnect(); state("unavailable"); });
    });
    setTimeout(() => pending.forEach(({ watch, state, container }) => {
      watch.disconnect();
      if (container.dataset.state === "loading") state("unavailable");
    }), 45000);
    return loading;
  };
  if (!("IntersectionObserver" in window)) { load(); return; }
  const visible = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) { visible.disconnect(); load(); }
  }, { rootMargin: "200px" });
  badges.forEach((badge) => visible.observe(badge.closest("article")));
})();
