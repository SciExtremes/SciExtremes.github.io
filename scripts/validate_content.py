#!/usr/bin/env python3
"""Validate shared records, display settings, translations, assets, and associations."""
from datetime import date
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import yaml

from content_model import ROOT, GROUPS, read_yaml, validate_records

errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


def load(path):
    try:
        return read_yaml(path)
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f'{path.relative_to(ROOT)}: {exc}')
        return {}


def valid_url(value, origin):
    value = str(value)
    try:
        url = urlsplit(value)
    except ValueError:
        errors.append(f'{origin}: invalid URL {value}')
        return
    require(url.scheme in ('https', 'mailto') or (value.startswith('/') and not url.netloc),
            f'{origin}: expected HTTPS, mailto, or a root-relative URL: {value}')
    if url.scheme == 'https':
        require(bool(url.netloc), f'{origin}: missing URL host')
    if value.startswith(('/uploads/', '/images/')) and not url.netloc:
        require(((ROOT / 'assets' if url.path.startswith('/images/') else ROOT / 'static') / url.path.lstrip('/')).is_file(),
                f'{origin}: missing local download {value}')


def valid_date(value, origin):
    try:
        date.fromisoformat(str(value))
    except ValueError:
        errors.append(f'{origin}: invalid date {value}')


records, record_errors = validate_records()
errors.extend(record_errors)
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
papers = records['publications']

for path in (ROOT / 'data/media').glob('*.yaml'):
    require(path.stem in papers, f'{path.name}: media needs an existing paper')
    coverage = load(path)
    require(isinstance(coverage, list), f'{path.name}: expected a media list')
    if isinstance(coverage, list):
        for item in coverage:
            require(isinstance(item, dict), f'{path.name}: each report must be an object')
            if not isinstance(item, dict):
                continue
            require(bool(item.get('outlet')) and bool(item.get('title')), f'{path.name}: missing outlet/title')
            valid_url(item.get('url', ''), path.name)

profile = load(ROOT / 'data/profile.yaml')
if 'author_names' in profile:
    require(isinstance(profile['author_names'], list) and bool(profile['author_names']) and all(isinstance(n, str) and n.strip() for n in profile['author_names']), 'profile.author_names: use nonempty formal name strings')
for lang in ('en', 'zh'):
    for key in ('name', 'role'):
        value = profile.get(lang, {}).get(key)
        require(isinstance(value, str) and bool(value.strip()), f'profile: missing {lang}.{key}')
    require(bool(profile.get('affiliation', {}).get('name', {}).get(lang)), f'profile: missing {lang} affiliation')
valid_url(profile.get('cv', ''), 'profile.cv')
require((ROOT / 'assets/images' / profile.get('portrait', '')).is_file(), 'missing profile portrait')
for link in profile.get('links', []):
    valid_url(link.get('url', ''), 'profile')
    require(set(link) == {'label', 'url', 'languages'}, 'profile link: use label, url and languages')
    languages = link.get('languages', [])
    require(isinstance(languages, list) and bool(languages) and set(languages) <= {'en', 'zh'}
            and len(languages) == len(set(languages)), 'profile link: invalid or duplicate languages')
require(len({l.get('label') for l in profile.get('links', [])}) == len(profile.get('links', [])),
        'profile: duplicate social link label')
valid_url(profile.get('affiliation', {}).get('url', ''), 'affiliation')
for item in profile.get('education', []):
    valid_date(item.get('start', ''), 'education')
    if item.get('end'):
        valid_date(item['end'], 'education')
    for lang in ('en', 'zh'):
        require(item.get('degree', {}).get(lang) and item.get('institution', {}).get(lang), f'education: missing {lang} text')
for item in profile.get('experience', []):
    valid_date(item.get('start', ''), 'experience')
    if item.get('end'):
        valid_date(item['end'], 'experience')
    if item.get('supervisor_url'):
        require(bool(item.get('supervisor')), 'experience: supervisor link needs a name')
        valid_url(item['supervisor_url'], 'experience.supervisor_url')
    if item.get('supervisor'):
        require(isinstance(item['supervisor'], dict) and set(item['supervisor']) == {'en', 'zh'}
                and all(isinstance(value, str) and value.strip() for value in item['supervisor'].values()),
                'experience: supervisor display name needs en/zh text')
    for unit in item.get('units', []):
        require(bool(unit.get('name')), 'experience: linked unit needs a name')
        valid_url(unit.get('url', ''), 'experience.units')
    for lang in ('en', 'zh'):
        require(item.get('role', {}).get(lang) and item.get('institution', {}).get(lang), f'experience: missing {lang} text')
focus = load(ROOT / 'data/focus.yaml')
for lang in ('en', 'zh'):
    require(len(focus.get(lang, {}).get('words', [])) == 3, f'focus: missing three {lang} directions')
    require(bool(focus.get(lang, {}).get('introduction')), f'focus: missing {lang}.introduction')

# Scientific questions own their prose and references; other records have no SQ fields.
layout = load(ROOT / 'data/research_layout.yaml')
require(isinstance(layout.get('framework_enabled'), bool), 'research_layout.framework_enabled: expected boolean')
paragraph_labels = layout.get('paragraph_labels', [])
require(isinstance(paragraph_labels, list) and len(paragraph_labels) == 3 and all(isinstance(v, str) and v for v in paragraph_labels), 'research_layout.paragraph_labels: expected three interface keys')
require(type(layout.get('representative_paper_limit')) is int and layout['representative_paper_limit'] > 0, 'research_layout.representative_paper_limit: expected positive integer')
style_stages = layout.get('stages', [])
require(isinstance(style_stages, list) and len(style_stages) == 4, 'research_layout.stages: four-stage preset needs four display settings')
for style in style_stages:
    require(set(style) == {'tone', 'icon', 'modulated'} and style['tone'] in ('blue', 'amber', 'green', 'slate') and style['icon'] in ('globe', 'cloud', 'forest', 'city') and type(style['modulated']) is bool, 'research_layout.stages: invalid tone/icon/modulated setting')
require(layout.get('modifier_group_size') == 2, 'research_layout.modifier_group_size: the preset groups two modifiers before the terminal modifier')
questions = load(ROOT / 'data/questions.yaml')
require(isinstance(questions, list) and bool(questions), 'questions: expected at least one research question')
require(len({q.get('id') for q in questions}) == len(questions) and all(re.fullmatch(r'[a-z][a-z0-9_-]*', str(q.get('id', ''))) for q in questions), 'questions: IDs must be unique lowercase anchor-safe keys')
require(not any(q.get('id') in {'main','questions-title','framework-title','framework-caption'} for q in questions), 'questions: IDs must not collide with layout landmarks')
question_ids = {q.get('id') for q in questions}
for q in questions:
    require({'id', 'title', 'paragraphs', 'paper_ids', 'data_ids'} <= set(q) <= {'id', 'label', 'title', 'paragraphs', 'paper_ids', 'data_ids'}, 'question: unknown or missing field')
    if 'label' in q:
        require(isinstance(q['label'], str) and bool(q['label'].strip()), 'question.label: expected nonempty short display label')
    title = q.get('title', {})
    require(isinstance(title, dict) and set(title) == {'en', 'zh'} and all(isinstance(v, str) and v.strip() for v in title.values()),
            f'{q.get("id")}: title needs en/zh text')
    paragraphs = q.get('paragraphs', {})
    require(isinstance(paragraphs, dict) and set(paragraphs) == {'en', 'zh'}, f'{q["id"]}: missing bilingual paragraphs')
    for lang in ('en', 'zh'):
        prose = paragraphs.get(lang, [])
        require(isinstance(prose, list) and len(prose) == len(paragraph_labels) and all(isinstance(v, str) and v.strip() for v in prose),
                f'{q["id"]}: three {lang} paragraphs should cover significance/objectives, methods/progress, and next steps')
    for field, group in (('paper_ids', 'publications'), ('data_ids', 'resources')):
        ids = q.get(field, [])
        require(isinstance(ids, list) and all(isinstance(x, str) and x in records[group] for x in ids) and len(set(ids)) == len(ids),
                f'{q["id"]}: {field} must reference unique known resources')
    require(len(q.get('paper_ids', [])) <= layout['representative_paper_limit'], f'{q["id"]}: too many representative papers for the configured limit')
for lang in ('en', 'zh'):
    require({p.relative_to(ROOT / f'content/{lang}/research') for p in (ROOT / f'content/{lang}/research').rglob('*.md')} == {Path('_index.md')}, 'Research content is a single overview page')

# Mechanism labels have one source and must be readable in both languages.
if layout['framework_enabled']:
    framework = load(ROOT / 'data/framework.yaml')
    def bilingual(value, origin):
        require(isinstance(value, dict) and all(isinstance(value.get(lang), str) and value[lang].strip()
                for lang in ('en', 'zh')), f'{origin}: missing bilingual text')
    for key in ('title', 'description', 'context', 'caption'):
        bilingual(framework.get(key), f'framework.{key}')
    stages = framework.get('stages', [])
    require(len(stages) == len(style_stages) and len({item.get('id') for item in stages}) == len(stages), 'framework: expected unique stage IDs matching the four-stage preset')
    for stage_index, item in enumerate(stages):
        bilingual(item.get('title'), f'framework.{item.get("id")}')
        require(bool(item.get('sq_ids')) and set(item['sq_ids']) <= question_ids, 'framework: stage needs known sq_ids')
        if stage_index > 0:
            bilingual(item.get('relation'), f'framework.{item.get("id")}.relation')
        require(bool(item.get('terms')), 'framework: each stage needs scientific terms')
        for term in item.get('terms', []):
            require(set(term) == {'label', 'detail', 'paper_id'},
                    'framework term: use label/detail and a representative paper_id')
            require(isinstance(term.get('paper_id'), str) and (not term['paper_id'] or term['paper_id'] in papers), 'framework term: paper_id must be empty or an existing published paper')
            for key in ('label', 'detail'):
                bilingual(term.get(key), f'framework.term.{key}')
    require(len(framework.get('modifiers', [])) == layout['modifier_group_size'] + 1 and len({item.get('id') for item in framework.get('modifiers', [])}) == len(framework.get('modifiers', [])), 'framework: expected unique modifiers for the preset display positions')
    for item in framework.get('modifiers', []):
        for key in ('title', 'detail', 'target'):
            bilingual(item.get(key), f'framework.{item.get("id")}.{key}')
    require(len(framework.get('foundation', [])) == 4, 'framework.foundation: four-stage preset needs four foundation columns')
    for item in framework.get('foundation', []):
        bilingual(item.get('title'), 'framework.foundation.title')
        for key in ('label', 'note'):
            if key in item:
                bilingual(item[key], f'framework.foundation.{key}')
        for value in item.get('lines', []):
            bilingual(value, 'framework.foundation.line')
        for ident in item.get('resource_ids', []):
            require(ident in records['resources'], f'framework: unknown data resource {ident}')
    for value in framework.get('legend', {}).values():
        bilingual(value, 'framework.legend')

paths = {}
for lang in ('en', 'zh'):
    base = ROOT / 'content' / lang
    paths[lang] = {p.relative_to(base) for p in base.rglob('*.md')}
    for path in base.rglob('*.md'):
        parts = path.read_text().split('---', 2)
        require(len(parts) == 3, f'{path}: missing YAML front matter')
        if len(parts) != 3:
            continue
        try:
            meta = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as exc:
            errors.append(f'{path}: {exc}')
            continue
        relative = path.relative_to(base)
        section = relative.parts[0]
        if path.name == '_index.md':
            require(set(meta) == {'title', 'description'}, f'{relative}: section metadata uses title and description')
        if relative == Path('about/index.md'):
            require(set(meta) == {'title', 'description', 'type'} and meta.get('type') == 'about', f'{relative}: About metadata uses title, description and type: about')
        if path.name == 'index.md' and section in GROUPS:
            ident = meta.get('record_id')
            require(ident in records[GROUPS[section]], f'{relative}: unknown record_id')
            require(ident == path.parent.name, f'{relative}: record_id must match page folder')
            require(not any(k in meta for k in ('display', 'date', 'image', 'doi', 'authors', 'journal', 'links', 'paper_ids')),
                    f'{relative}: facts and display controls belong in shared data')
            require(set(meta) <= {'record_id', 'title', 'summary', 'description', 'translated_title', 'image_caption'},
                    f'{relative}: unknown localized content field')
            if section == 'publications':
                require('title' not in meta, f'{relative}: the formal title belongs in shared data')
            else:
                require(bool(meta.get('title')), f'{relative}: missing localized title')
        require(bool(meta.get('title') or meta.get('record_id')), f'{relative}: missing title/record_id')
require(paths['en'] == paths['zh'], 'English and Chinese page paths differ')
for section, group in GROUPS.items():
    for ident in records[group]:
        require(Path(f'{section}/{ident}/index.md') in paths['en'], f'{ident}: missing paired content pages')
hero = load(ROOT / 'data/home.yaml')['hero']
require((ROOT / 'assets/images' / hero['image']).is_file(), 'missing home hero')
valid_url(hero.get('source_url', ''), 'home.hero.source_url')
for lang in ('en', 'zh'):
    require(bool(hero.get('source_label', {}).get(lang)), f'home.hero: missing {lang} source credit')

# A label is maintained in both languages, so new resource buttons cannot fall back silently.
translations = {lang: load(ROOT / f'i18n/{lang}.yaml') for lang in ('en', 'zh')}
require(translations['en'].keys() == translations['zh'].keys(), 'Interface translation keys differ')
for lang, values in translations.items():
    for key, value in values.items():
        require(isinstance(value, dict) and isinstance(value.get('other'), str) and value['other'].strip(),
                f'i18n/{lang}: {key} needs a nonempty translation')
    for key in paragraph_labels + ['frameworkPaper']:
        require(key in values, f'i18n/{lang}: missing shared Research label {key}')
    require(values.get('frameworkPaper', {}).get('other', '').count('%s') == 2,
            f'i18n/{lang}: frameworkPaper needs term and paper title placeholders')
for link in profile.get('links', []):
    require(link.get('label') in translations['en'], 'profile link: label needs both translations')
for group in records.values():
    for record in group.values():
        links = record.get('links', [])
        for link in links if isinstance(links, list) else []:
            if isinstance(link, dict):
                require(link.get('label') in translations['en'], f'{record["id"]}: resource label needs both translations')

# Track every authored asset reference, including Markdown, render hooks and figures.
used_images = {r['image'] for group in records.values() for r in group.values() if r.get('image')}
used_images.update((profile['portrait'], hero['image'], 'icon.png'))
used_downloads = {urlsplit(profile['cv']).path}
used_downloads.update(urlsplit(link['url']).path for group in records.values() for r in group.values() for link in r['links'] if link['url'].startswith('/uploads/'))
from urllib.parse import unquote
for path in (ROOT / 'content').rglob('*.md'):
    prose = path.read_text()
    for ref in re.findall(r'(?:\]\(|(?:src|href)=\")([^\s)\"]+)', prose):
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            continue
        target = unquote(parsed.path)
        if target.startswith('/uploads/'):
            used_downloads.add(target)
            require((ROOT / 'static' / target.lstrip('/')).is_file(), f'{path.relative_to(ROOT)}: missing attachment {target}')
        elif target.startswith('/images/'):
            used_images.add(target.removeprefix('/images/'))
            require((ROOT / 'assets' / target.lstrip('/')).is_file(), f'{path.relative_to(ROOT)}: missing image {target}')
        elif target and not target.startswith('/'):
            require((path.parent / target).is_file(), f'{path.relative_to(ROOT)}: missing local page asset {target}')
    for ref in re.findall(r'^\s*\[[^]]+\]:\s*(\S+)', prose, re.M):
        target = unquote(urlsplit(ref.strip('<>')).path)
        if target.startswith('/uploads/'):
            used_downloads.add(target)
            require((ROOT / 'static' / target.lstrip('/')).is_file(), f'{path}: missing attachment {target}')
        elif target.startswith('/images/'):
            used_images.add(target.removeprefix('/images/'))
            require((ROOT / 'assets' / target.lstrip('/')).is_file(), f'{path}: missing image {target}')
    for ref in re.findall(r'{{<\s*figure\b[^>]*?\bsrc=[\"\']([^\"\']+)', prose):
        target = unquote(urlsplit(ref).path)
        if target.startswith('/images/'):
            used_images.add(target.removeprefix('/images/'))
            require((ROOT / 'assets' / target.lstrip('/')).is_file(), f'{path}: missing figure {target}')
source_images = {p.relative_to(ROOT / 'assets/images').as_posix() for p in (ROOT / 'assets/images').rglob('*') if p.is_file()}
require(source_images == used_images, f'Images: unreferenced or missing assets: {sorted(source_images ^ used_images)}')
source_downloads = {'/uploads/' + p.relative_to(ROOT / 'static/uploads').as_posix() for p in (ROOT / 'static/uploads').rglob('*') if p.is_file()}
require(source_downloads == used_downloads, f'Downloads: unreferenced or missing files: {sorted(source_downloads ^ used_downloads)}')

if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Content OK: {sum(map(len, records.values()))} shared records; {len(paths["en"])} paired pages; display settings and associations valid.')
