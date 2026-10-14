# Testing

[简体中文](../zh/testing.md)

Run checks against freshly built output:

```bash
npm run check:content
npm run build
npm run check
```

| Command | Scope |
|---|---|
| `check:docs` | Paired README/docs, section structure, technical examples, language links, local files and anchors |
| `check:content` | Fields, types, defaults, IDs, paired pages, associations, assets, profile and Research structure |
| `check:model` | Supported record types, optional fields, actionable failures and normalization |
| `check:interactions` | Menu/focus behavior, search loading/failure, metadata escaping and Altmetric states |
| `check:links` | Built URLs, fragments, XML, citations, navigation, selection labels, year-local feature priority, consistent home/section paper sequence, display controls and Research references |
| `check:scenarios` | Disposable builds of supported content types at root and project paths |
| `check:template` | Different profile, content, IDs, navigation order and optional framework in a disposable clone |
| `check:browser` | Actual browser rendering, responsive layout, search, keyboard and simulated touch |

`check` runs docs, content, model, interaction and output checks. Output checks require `public/`; rebuilding first prevents testing stale pages. Nonzero exit status indicates a failure. Correct the reported path, field or URL and rerun the relevant check.

## Browser setup

```bash
npx playwright install --with-deps chromium
npm run check:browser
```

For multiple engines:

```bash
npx playwright install --with-deps chromium firefox webkit
TEST_BROWSERS=chromium,firefox,webkit npm run check:browser
```

Tests derive navigation and languages from generated HTML. Search queries come from indexed page titles instead of a particular research subject. Homepage/section layouts cover 320, 390, 520, 521, 760, 761, 768, 1000, 1001, 1024, 1279, 1280, 1440 and 1920px. Detail pages cover 390/768/1440px. Additional checks exercise landscape, doubled text, Escape/focus, local search, no-JavaScript navigation and supported simulated touch contexts.

`TEST_SITE_DIR` selects another build directory. `TEST_SCREENSHOTS` selects an optional absolute screenshot directory; by default tests do not write screenshots. Keep generated screenshots outside source or in ignored `test-results/`.

Browsers render build bytes without external requests. External publication pages and live Altmetric scores need separate checks. Browser engines and simulated viewports do not constitute physical iOS/Android or macOS Safari device testing.

## Content and customization scenarios

```bash
npm run check:scenarios
npm run check:template
```

Tests create temporary copies, validate/build them and remove them on exit. Production content is not changed. Scenarios cover publication types/statuses, date precision, oral/keynote reports, resources, citations, SVG/GIF, attachments, versions and content creation. They also cover multiple featured papers, formal/fallback-year groups, features before ordinary priorities, relative sequence when only some features appear at home, cross-year homepage sorting, hidden/no selections and stable ties in priority/date. Template checks replace site-specific values and disable the optional framework to verify configuration independence.

Add browser coverage to temporary scenarios:

```bash
TEST_SCENARIO_BROWSER=1 npm run check:scenarios
TEST_TEMPLATE_BROWSER=1 npm run check:template
```

## Project paths and visual review

```bash
HUGO_BASEURL=https://example.org/academic-site/ npm run build
npm run check
npm run check:browser
```

Rebuild without the environment override to return to the configured URL. Review container alignment, headings, complete scientific figures, long names/titles, grouped actions, Research term links and language switching at several sizes. Confirm PDF behavior and external links after deployment.

GitHub Actions runs documentation, content, model, interaction, scenario and template checks, then builds production output and checks links and Chromium rendering. Dependency versions live in the lock file, requirements and workflow. Pull requests validate; publishing occurs only after successful checks on the deployment path.
