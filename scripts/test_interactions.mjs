/* Small DOM doubles exercise failure cases without a browser or test dependency. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { runInNewContext } from "node:vm";

const readScript = (name) => readFileSync(new URL(`../assets/js/${name}.js`, import.meta.url), "utf8");
const settle = () => new Promise((resolve) => setImmediate(resolve));

function badgeScenario({ image = null, hiddenByVendor = false, blocked = false, lazy = false } = {}) {
  const fallback = { hidden: false, setAttribute(_name, value) { this.label = value; } };
  const container = { dataset: { loading: "Loading", empty: "No score", unavailable: "Unavailable" },
    querySelector: () => fallback };
  const article = {};
  let mutation;
  let intersection;
  let observed;
  let requests = 0;
  let timeout;
  const badge = {
    style: { display: hiddenByVendor ? "none" : "" },
    closest: (selector) => selector === "article" ? article : container,
    querySelector: () => image,
  };
  const imageHandlers = {};
  if (image) image.addEventListener = (name, callback) => { imageHandlers[name] = callback; };
  const window = { _altmetric_embed_init: () => mutation() };
  const context = {
    window,
    document: {
      querySelectorAll: () => [badge],
      createElement: () => ({}),
      head: { append(script) { requests += 1; blocked ? script.onerror() : script.onload(); } },
    },
    MutationObserver: class {
      constructor(callback) { mutation = callback; }
      observe() {}
      disconnect() {}
    },
    setTimeout(callback) { timeout = callback; },
  };
  if (lazy) {
    window.IntersectionObserver = true;
    context.IntersectionObserver = class {
      constructor(callback) { intersection = callback; }
      observe(element) { observed = element; }
      disconnect() {}
    };
  }
  runInNewContext(readScript("altmetric"), context);
  return { container, fallback, article, imageHandlers, expire: () => timeout(), requests: () => requests,
    unhide: () => { badge.style.display = ""; mutation(); },
    observed: () => observed, intersect: () => intersection([{ isIntersecting: true }]) };
}

test("a real loaded badge replaces the empty ring", async () => {
  const scenario = badgeScenario({ image: { complete: true, naturalWidth: 64 } });
  await settle();
  assert.equal(scenario.fallback.hidden, true);
  assert.equal(scenario.requests(), 1);
});

test("missing and zero scores retain an empty ring without a number", async () => {
  const missing = badgeScenario();
  const zero = badgeScenario({ image: { complete: true, naturalWidth: 64 }, hiddenByVendor: true });
  await settle();
  assert.equal(missing.fallback.hidden, false);
  assert.equal(zero.fallback.hidden, false);
  assert.equal(zero.container.dataset.state, "empty");
  assert.equal(zero.fallback.label, "No score");
  missing.expire();
  assert.equal(missing.container.dataset.state, "unavailable");
});

test("blocked scripts and failed images preserve the empty ring", async () => {
  const blocked = badgeScenario({ blocked: true });
  const failed = badgeScenario({ image: { complete: true, naturalWidth: 0 } });
  await settle();
  failed.imageHandlers.error();
  assert.equal(blocked.fallback.hidden, false);
  assert.equal(failed.fallback.hidden, false);
  assert.equal(blocked.fallback.label, "Unavailable");
  assert.equal(failed.fallback.label, "Unavailable");
});

test("a vendor-revealed cached image replaces the ring after an initial hidden state", async () => {
  const scenario = badgeScenario({ image: { complete: true, naturalWidth: 64 }, hiddenByVendor: true });
  await settle();
  assert.equal(scenario.fallback.hidden, false);
  scenario.unhide();
  assert.equal(scenario.fallback.hidden, true);
});

test("the ring stays visible until the official image has loaded", async () => {
  const image = { complete: false, naturalWidth: 0 };
  const scenario = badgeScenario({ image });
  await settle();
  assert.equal(scenario.fallback.hidden, false);
  image.naturalWidth = 64;
  scenario.imageHandlers.load();
  assert.equal(scenario.fallback.hidden, true);
});

test("lazy loading requests badges when their article becomes visible", async () => {
  const scenario = badgeScenario({ lazy: true });
  assert.equal(scenario.requests(), 0);
  assert.equal(scenario.observed(), scenario.article);
  scenario.intersect();
  await settle();
  assert.equal(scenario.requests(), 1);
});

function navigationScenario() {
  const handlers = {};
  const classes = new Set();
  let expanded = "false";
  let focused = false;
  const button = {
    getAttribute: () => expanded,
    setAttribute: (_name, value) => { expanded = value; },
    addEventListener: (name, callback) => { handlers[name] = callback; },
    focus: () => { focused = true; },
  };
  const navigation = {
    classList: {
      remove: (name) => classes.delete(name),
      contains: (name) => classes.has(name),
      toggle(name, enabled) { enabled ? classes.add(name) : classes.delete(name); },
    },
    addEventListener: (_name, callback) => { handlers.link = callback; },
  };
  runInNewContext(readScript("navigation"), {
    document: {
      getElementById: (id) => id === "menu-toggle" ? button : navigation,
      documentElement: { classList: { add() {} } },
      addEventListener: (_name, callback) => { handlers.key = callback; },
    },
    matchMedia: () => ({ addEventListener: (_name, callback) => { handlers.resize = callback; } }),
  });
  return { handlers, expanded: () => expanded, open: () => classes.has("is-open"), focused: () => focused };
}

test("Escape closes compact navigation and returns keyboard focus", () => {
  const scenario = navigationScenario();
  scenario.handlers.click();
  assert.equal(scenario.open(), true);
  assert.equal(scenario.expanded(), "true");
  scenario.handlers.key({ key: "Escape" });
  assert.equal(scenario.open(), false);
  assert.equal(scenario.expanded(), "false");
  assert.equal(scenario.focused(), true);
});

test("following a link or changing viewport closes compact navigation", () => {
  const scenario = navigationScenario();
  scenario.handlers.click();
  scenario.handlers.link({ target: { closest: () => ({}) } });
  assert.equal(scenario.open(), false);
  scenario.handlers.click();
  scenario.handlers.resize();
  assert.equal(scenario.expanded(), "false");
});

function searchScenario({ blocked = false } = {}) {
  const handlers = {};
  let requests = 0;
  let options;
  let focused = 0;
  const input = { focus() { focused += 1; } };
  const opener = { addEventListener(_name, callback) { handlers.open = callback; }, focus() { focused += 1; } };
  const results = { textContent: "", querySelector: () => input };
  const dialog = {
    dataset: { assets: "/preview/pagefind/", language: "en", unavailable: "Search unavailable" },
    open: false,
    showModal() { this.open = true; },
    close() { this.open = false; handlers.close(); },
    addEventListener(name, callback) { handlers[name] = callback; },
    getBoundingClientRect: () => ({ left: 0, right: 100, top: 0, bottom: 100 }),
  };
  runInNewContext(readScript("search"), {
    window: { PagefindUI: class { constructor(config) { options = config; } } },
    document: {
      getElementById: (id) => id === "search-dialog" ? dialog : results,
      querySelectorAll: () => [opener],
      querySelector: () => ({ addEventListener(_name, callback) { handlers.dismiss = callback; } }),
      createElement: (tag) => ({ tag }),
      head: { append(element) { if (element.tag === "script") { requests += 1; blocked ? element.onerror() : element.onload(); } } },
    },
  });
  return { handlers, dialog, results, options: () => options, requests: () => requests, focused: () => focused };
}

test("search loads once, keeps project paths, and returns focus when closed", async () => {
  const scenario = searchScenario();
  await scenario.handlers.open();
  assert.equal(scenario.dialog.open, true);
  assert.equal(scenario.options().bundlePath, "/preview/pagefind/");
  assert.equal(scenario.focused(), 1);
  scenario.handlers.dismiss();
  assert.equal(scenario.focused(), 2);
  await scenario.handlers.open();
  assert.equal(scenario.requests(), 1);
});

test("blocked search assets show a readable fallback", async () => {
  const scenario = searchScenario({ blocked: true });
  await scenario.handlers.open();
  assert.equal(scenario.results.textContent, "Search unavailable");
});

test("search metadata is escaped and does not alter cached result excerpts", async () => {
  const scenario = searchScenario();
  await scenario.handlers.open();
  const result = { meta: { section: "<Data & code>", date: "May 2025" }, excerpt: "A <mark>match</mark>" };
  const rendered = scenario.options().processResult(result);
  assert.match(rendered.excerpt, /&lt;Data &amp; code&gt; · May 2025/);
  assert.match(rendered.excerpt, /<mark>match<\/mark>/);
  assert.equal(result.excerpt, "A <mark>match</mark>");
});
