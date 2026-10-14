# SciExtremes

[简体中文](README.md)

A bilingual academic website built with native Hugo. Shared YAML records supply facts and display settings; English and Chinese Markdown pages supply localized prose. The site includes research, publications, resources, presentations, news and a profile, with responsive layouts and local search.

## Quick start

Requirements: Hugo **0.161.1** (standard edition), Node.js **22+**, Python **3.10+**. Commands use a POSIX shell, available on Linux, macOS and Windows through WSL.

```bash
npm ci --ignore-scripts
python3 -m pip install -r requirements.txt
npm run check:content
npm run build
npm run check
npm run dev
```

`build` generates HTML and the Pagefind search index. Rebuild after changing content so search results match the site. The development server prints its local address.

## Customize

| Purpose | Location |
|---|---|
| Site URL and output settings | `config/_default/hugo.yaml` |
| Languages, navigation and date formats | `config/_default/` and `i18n/` |
| Profile, affiliation, links, portrait, CV and appointments | `data/profile.yaml` |
| Home introduction, keywords and background credits | `data/focus.yaml` and `data/home.yaml` |
| Research prose and references | `data/questions.yaml` and `data/framework.yaml` |
| Research framework display preset | `data/research_layout.yaml` |
| Record fields, defaults and supported types | `data/content_schema.yaml` |
| Publication, resource, presentation and news facts | Corresponding folders in `data/` |
| Localized titles, summaries, prose and captions | `content/en/` and `content/zh/` |
| Images and public attachments | `assets/images/` and `static/uploads/` |
| Shared styles and components | `assets/` and `layouts/` |

The bundled academic content belongs to its named authors and sources. When creating another site, replace the profile, content and assets with your own materials and update their credits. The code license does not grant rights to third-party figures or photographs.

Homepage highlights use `display.home` and require `display.featured: true`. Several publications can be featured at the top of their respective year groups. Homepage and Publications share year, featured state, `display.order`, date and ID sorting; filtering homepage papers preserves their relative sequence. See the [content guide](docs/en/content-guide.md) for complete rules.

## Add content

```bash
npm run new -- presentations sample-talk --date 2027-01-01 --title-en "Presentation title" --title-zh "报告题目" --event "Example meeting" --kind oral
```

The command creates a shared record and both language pages, refusing to overwrite existing IDs. Complete the prose, select visibility, then validate and build. Field rules and examples are in the [content guide](docs/en/content-guide.md).

## Checks

```bash
npm run check:scenarios
npx playwright install --with-deps chromium
npm run check:browser
```

Scenario tests build supported content types in a disposable directory. Browser checks cover responsive layouts, enlarged text, menus, search and touch interactions. See [Testing](docs/en/testing.md) for full instructions.

## Documentation

- [Deployment](docs/en/deployment.md)
- [Content guide](docs/en/content-guide.md)
- [Testing](docs/en/testing.md)
- [Credits](docs/en/credits.md)
- [Code license](LICENSE.md)

Generated output, dependencies, caches and test screenshots are excluded from source control. Include `.github/` and `.gitignore` when copying source into a new repository.
