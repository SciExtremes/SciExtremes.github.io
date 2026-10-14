/* Search assets stay local and are loaded only when the dialog is opened. */
(() => {
  const dialog = document.getElementById("search-dialog");
  const results = document.getElementById("search-results");
  let loading;
  let opener;
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
  function loadSearch() {
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {
      const css = document.createElement("link");
      css.rel = "stylesheet";
      css.href = `${dialog.dataset.assets}pagefind-ui.css`;
      document.head.append(css);
      const script = document.createElement("script");
      script.src = `${dialog.dataset.assets}pagefind-ui.js`;
      script.onload = resolve;
      script.onerror = reject;
      document.head.append(script);
    })
      .then(() => {
        new window.PagefindUI({
          element: "#search-results",
          bundlePath: dialog.dataset.assets,
          showSubResults: false,
          showImages: false,
          showEmptyFilters: false,
          processResult(result) {
            // Page metadata identifies a result without duplicating its heading or excerpt.
            const metadata = [result.meta.section, result.meta.date].filter(Boolean).map(escapeHtml).join(" · ");
            return { ...result, excerpt: metadata ? `<span class="search-result-meta">${metadata}</span>${result.excerpt}` : result.excerpt };
          },
          translations:
            dialog.dataset.language === "zh"
              ? {
                  placeholder: "搜索",
                  clear_search: "清除",
                  load_more: "加载更多",
                  search_label: "搜索本站",
                  zero_results: "未找到与 [SEARCH_TERM] 相关的结果",
                  many_results: "找到 [COUNT] 条结果",
                  one_result: "找到 1 条结果",
                  searching: "正在搜索…",
                }
              : {},
        });
      })
      .catch(() => {
        results.textContent = dialog.dataset.unavailable;
      });
    return loading;
  }
  document.querySelectorAll("[data-search-open]").forEach((button) => {
    button.addEventListener("click", async () => {
      opener = button;
      dialog.showModal();
      await loadSearch();
      if (dialog.open) results.querySelector("input")?.focus();
    });
  });
  document
    .querySelector("[data-search-close]")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    const box = dialog.getBoundingClientRect();
    if (
      event.target === dialog &&
      (event.clientX < box.left ||
        event.clientX > box.right ||
        event.clientY < box.top ||
        event.clientY > box.bottom)
    )
      dialog.close();
  });
  dialog.addEventListener("close", () => opener?.focus());
})();
