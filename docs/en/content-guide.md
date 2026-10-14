# Content guide

[简体中文](../zh/content-guide.md)

Shared records own facts and display settings. English and Chinese Markdown pages own localized prose. Store each fact once and reference related records by stable ID. Replace sample IDs and paths with actual records and materials; examples are not installed site content.

## Files and IDs

| Section | Shared record | Localized pages |
|---|---|---|
| Publications | `data/publications/{id}.yaml` | `content/{en,zh}/publications/{id}/index.md` |
| Data | `data/resources/{id}.yaml` | `content/{en,zh}/data/{id}/index.md` |
| Presentations | `data/presentations/{id}.yaml` | `content/{en,zh}/presentations/{id}/index.md` |
| News | `data/news/{id}.yaml` | `content/{en,zh}/news/{id}/index.md` |

ID, YAML filename, page folder and `record_id` must match. IDs remain stable when titles, dates or status change. Case-only collisions are rejected because output paths are lowercase. English uses the root path; Chinese uses `/zh/`.

```markdown
---
record_id: sample-talk
title: Localized title
summary: Localized summary
image_caption: Localized caption
---

Public description or abstract.
```

Publication pages use the shared formal title instead of Markdown `title`; Chinese pages may add `translated_title`. Display settings, authors, dates, DOI, links and main images belong in YAML.

## Common fields and display

`id / date` are required. Optional values and defaults are defined in [the schema](../../data/content_schema.yaml), read by Hugo and Python. Explicit values override defaults, including `false`.

| Field | Meaning |
|---|---|
| `date` | Source-supported date in `YYYY-MM-DD` form |
| `date_precision` | `day` (default), `month` or `year` |
| `end_date` | Optional end of a range, using the same precision |
| `updated` | Optional resource update date, displayed at day precision |
| `image` | Path relative to `assets/images/`; omitted when unused |
| `image_fit` | `contain` (default) or `cover`; scientific figures/interfaces use `contain` |
| `image_alt.en / zh` | Image descriptions; empty values fall back to localized title |
| `links` | Ordered `label / url` objects; optional bilingual `name` and boolean `download` |
| `paper_ids` | Related publication IDs; empty by default |

For month precision use `YYYY-MM-01`; for year precision use `YYYY-01-01`. These values support sorting; visible dates and time metadata only show known precision. End/update dates cannot precede the start date. RSS omits full timestamps for month/year precision.

| `display` field | Default | Meaning |
|---|---|---|
| `visible` | `true` | Included in lists, home selections, relations, search, RSS and sitemap |
| `featured` | `false` | Section selection; several publications, at most one visible selection per other type |
| `home` | `false` | Homepage highlight; must also be a section selection |
| `order` | `0` | Shared display priority; positive values precede automatic date order, smaller positive values first |
| `image` | `false` | Enables the shared main image |
| `media` | `false` | Publications only: media coverage |
| `attention` | `false` | Publications only: Altmetric when DOI is available |

Homepage highlights are selected from section features: `home: true` requires `featured: true`, even for a temporarily hidden record. A section feature need not appear on the homepage. Validation reports contradictory settings without silently overriding explicit values. Homepage labels use Highlights; section labels use Featured. Both use the same titles, summaries, facts and materials. Selection does not automatically enable images, media coverage or attention.

Publications are grouped by year descending, with featured papers before ordinary papers within each year. Within the same year and featured state, compare `order` (positive first, smaller first), then date descending and stable ID ascending. Ordinary papers cannot use `order` to precede featured papers, and selection does not override year groups. Publications use formal `year` when available; otherwise they use the source date year and retain status descriptions. Each paper appears once in the complete bibliography.

Homepage section order is Publications, Data, Presentations, News. Homepage papers filter records with `home: true` from the already ordered Publications list, preserving relative sequence. Since all homepage papers are featured, their effective order is year descending, `order`, date descending and stable ID ascending. An older year's priority cannot override a newer year. The views may show different numbers of papers but share one ordering. Omitted `order` defaults to `0` and automatic date order within a group; equal positive priorities also fall back to date and ID for stable ordering.

Data, Presentations and News each allow at most one visible section feature and one visible homepage highlight. A homepage highlight must be the same record as the section's top feature. A section feature can exist without a homepage highlight. These three sections remove features from ordinary year lists to avoid duplication; ordinary lists use year, `order`, date and ID. Publications can have several visible features and homepage highlights. Quantity limits count visible records only.

```yaml
display:
  visible: true
  featured: true
  home: true
  order: 10
  image: false
```

Hidden records still produce accessible detail pages with `noindex`; visibility is not access control. Do not store private material in source. Future dates do not schedule publication; visibility controls discoverability.

## Links, associations and materials

Labels are interface keys in both `i18n` files. Optional `name.en / zh` distinguishes similar resources. The first action is primary; duplicate URLs in a group are removed in order. HTTPS, `mailto:` and site-relative URLs are supported.

```yaml
links:
  - label: accessData
    url: https://example.org/dataset
    name:
      en: Historical dataset
      zh: 历史数据集
  - label: documentation
    url: https://example.org/documentation
```

Media lists use `data/media/{paper-id}.yaml`, with `outlet / title / url`. Prose can use `{{< media paper="sample-paper" >}}` and `{{< paper id="sample-paper" >}}` to resolve shared media and formal titles. IDs must exist; hidden targets leave related link groups.

```markdown
![Image description](/images/example/figure.svg)
[Supplement](/uploads/supplement.pdf)
{{< figure src="/images/example/figure.svg" alt="Image description" caption="Figure caption" >}}
```

Global images live in `assets/images/`, downloads in `static/uploads/`. PNG/JPEG/WebP are optimized; SVG/GIF retain vector/animation data. Main and detail images share descriptions; captions are separate. Page-local assets may live beside `index.md` and use relative links. Checks track main images, inline/reference-style links, figure shortcodes and attachments. Remove unused assets when deleting content.

## Publications

Required fields: `title / authors`. Defaults: `type: article / status: published`. Authors are complete formal names, without role symbols or titles.

| `type` | Required when published or online first | BibTeX |
|---|---|---|
| `article` | `journal / year` | `@article` |
| `conference` | `booktitle / year` | `@inproceedings` |
| `preprint` | Matching `status: preprint`; optional `repository` | `@misc` |
| `chapter` | `booktitle / year` | `@incollection` |
| `report` | `institution / year` | `@techreport` |

Statuses: `published / online_first / accepted / preprint`. Accepted works and preprints may omit formal year; grouping and BibTeX use the source date year with a status note. Fill confirmed information when available. Online date and formal publication year may differ.

Optional fields: `doi / url / volume / number / pages / article_number / booktitle / publisher / institution / repository / identifier / author_roles / related_version_ids`. Use `pages` or `article_number`, not both; article numbers export as `eid`. DOI is bare. Without DOI, use `url` or `links`; DOI action and Altmetric are omitted. Citation download and title/author metadata remain available. Altmetric shows only officially loaded scores; unavailable scores use an empty neutral ring.

```yaml
id: sample-paper
date: '2027-01-01'
title: Example academic study
authors: [Example Researcher, Coauthor Name]
status: accepted
author_roles:
  equal_contribution: [Example Researcher, Coauthor Name]
  corresponding: [Example Researcher]
```

Roles reference exact authors and display `* / †` with descriptions. Citation names stay unmarked. Optional `profile.author_names: [Example Researcher, E. Researcher]` controls self-name emphasis; otherwise it matches the profile English name.

`related_version_ids` links records in the same group. Update a record to retain its URL, or keep associated versions separately. Two visible versions are listed separately; no automatic count/merge applies. Resource URLs belong to Data and are collected into related publications.

## Presentations

`event / kind` are required. Location, event URL, images, materials and paper associations are optional. Use source-supported information.

| Field | Supported values |
|---|---|
| `kind` | `poster / oral / seminar / lightning / other` |
| `event_type` | `conference / seminar / workshop / other`, or omitted |
| `role` | `contributed / invited / keynote`, or omitted |
| `participation` | `onsite / online / hybrid`, or omitted |

`other` requires nonempty `kind_label.en / zh`. Optional `event_label / location_label` provide display translations. `oral + seminar` displays Seminar; invited adds an invitation label. Keynote requires oral/seminar format. Online/hybrid participation is shown; standard onsite/contributed roles do not add redundant labels.

```yaml
id: sample-talk
date: '2027-05-02'
end_date: '2027-05-04'
event: Example seminar
kind: oral
event_type: seminar
role: invited
participation: online
```

## Resources and news

Data requires a shared `name`. Optional `resource_type`: `dataset / code / software / tool / other`. Metadata includes `version / license / doi / updated / related_version_ids`.

Structured `citation` requires `title / authors / year`, and supports `publisher / doi / url`. It generates a detail citation and `@misc` download. Resource/citation DOI must agree when both are present.

```yaml
id: sample-dataset
date: '2027-01-01'
name: Example dataset
resource_type: dataset
version: '2.0'
license: CC BY 4.0
citation:
  title: Example dataset title
  authors: [Example Researcher]
  year: 2027
  publisher: Example archive
```

Explain coverage, definitions, versions, usage and citation in localized prose. News can use `paper_ids / presentation_ids`; presentation materials remain in their own records.

## Research and profile

`data/questions.yaml` owns question titles, prose and representative references. IDs are unique lowercase anchor-safe keys, ordered by the list. Optional `label` provides a short displayed label independently of its anchor ID. Each question has three localized paragraphs and `paper_ids / data_ids`, which can be empty. Shared headings identify significance/objectives, approach/progress and next steps. Question IDs and links stay within Research.

Desktop places labels left and prose right; phones place labels above titles. Title, paragraphs and references share a text column. Avoid paragraph-specific widths and manual language-specific line breaks.

`data/framework.yaml` owns framework text and references. Each term uses bilingual `label / detail` and optional `paper_id`. Associate a paper only when the concept is a main research object, analysis or result. Same-level terms use equal typography; associated papers add an arrow. Hidden papers leave terms visible without links.

`data/research_layout.yaml` supplies display settings independently of scientific IDs: framework visibility, paragraph label keys, representative paper limit, stage icons/colors and modulated connections. The four-stage preset uses four stages/foundation columns and three modifiers, grouping the first two. It does not require particular stage/modifier names. Set `framework_enabled: false` for a text-only overview; `data/framework.yaml` can then be omitted. The three-paragraph question structure remains. Change a preset and its renderer together for another diagram topology.

Home keywords/introduction live in `data/focus.yaml`; background and credits in `data/home.yaml`. Profile, affiliation, education, appointments, CV and social links live in `data/profile.yaml`. One CV path supplies Home/About; `languages` selects social links. Supervisor display names can contain titles; publication names should not.

Navigation order lives in `config/_default/menus.yaml`, labels in `i18n`. Fonts, colors, spacing and container widths use shared CSS tokens. Scientific figures remain uncropped. All screen sizes read the same prose.

## Create and delete records

```bash
npm run new -- presentations sample-talk --date 2027-01-01 --title-en "Presentation title" --title-zh "报告题目" --event "Example meeting" --kind oral
npm run new -- publications sample-paper --date 2027-01-01 --title-en "Official title" --title-zh "辅助译名" --author "Example Researcher" --status accepted
npm run new -- data sample-resource --date 2027-01-01 --title-en "Resource description" --title-zh "资源介绍" --name "Example resource"
npm run new -- news sample-story --date 2027-01-01 --precision year --title-en "News title" --title-zh "动态标题"
```

The generator creates YAML and EN/ZH pages, refusing overwrites/case collisions. Generated records explicitly use `visible: false`; complete public prose and choose visibility before building. `archetypes/` provides Markdown-only helpers for manual maintenance.

Delete the shared record and both pages, clean Research/media/record/shortcode references, then remove unused assets. Validate, build and run checks as described in [Testing](testing.md).
