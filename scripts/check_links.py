#!/usr/bin/env python3
"""Check generated internal URLs, fragments, translated navigation, and HTML landmarks.

Checks local output only; external websites are never requested.
"""
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET
import yaml
from content_model import normalize, record_year

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'public').resolve()
errors = []
base_path = '/'
site_host = ''
source = Path(__file__).resolve().parents[1]
profile = yaml.safe_load((source / 'data/profile.yaml').read_text())
cv_path = urlsplit(profile['cv']).path
questions = yaml.safe_load((source / 'data/questions.yaml').read_text())
question_ids = {q['id'] for q in questions}
research_layout = yaml.safe_load((source / 'data/research_layout.yaml').read_text())
navigation = sorted(yaml.safe_load((source / 'config/_default/menus.yaml').read_text())['main'], key=lambda entry: entry.get('weight', 0))
sections = [entry['pageRef'].strip('/') for entry in navigation]


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.ordered_ids = []
        self.links = []
        self.canonical = ''
        self.share_image = ''
        self.h1 = 0
        self.main = 0
        self.lang = ''
        self.badges = []
        self.footer_text = []
        self.in_footer = False
        self.div_depth = 0
        self.action_groups = []
        self.search_trigger = False
        self.search_metadata = {}
        self.in_primary_nav = False
        self.navigation_links = []
        self.social_links = []
        self.in_social = False
        self.question_resources = {}
        self.question_paragraphs = {}
        self.question_subheadings = {}
        self.in_question_subheading = False
        self.active_question = ''
        self.framework_papers = []
        self.feature_labels = []
        self.in_feature_label = False
        self.active_publication = ''
        self.publication_labels = {}
        self.in_publication_label = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('property') == 'og:image':
            self.share_image = a.get('content', '')
            self.links.append(self.share_image)
        classes = a.get('class', '').split()
        if tag == 'article' and 'publication' in classes:
            self.active_publication = a.get('id', '')
        if tag == 'p' and self.active_publication and 'publication-featured' in classes:
            self.in_publication_label = True
            self.publication_labels[self.active_publication] = []
        if tag == 'article' and a.get('id') in question_ids:
            self.active_question = a['id']
            self.question_resources[a['id']] = []
            self.question_paragraphs[a['id']] = 0
            self.question_subheadings[a['id']] = []
        if tag == 'h4' and self.active_question and 'question-subheading' in classes:
            self.in_question_subheading = True
        if tag == 'p' and self.active_question and 'question-number' not in classes:
            self.question_paragraphs[self.active_question] += 1
        if tag == 'a' and self.active_question:
            self.question_resources[self.active_question].append(a.get('href'))
        if tag == 'a' and 'framework-paper-link' in classes:
            self.framework_papers.append(a.get('href'))
        if tag == 'ul' and 'social-links' in classes:
            self.in_social = True
        if tag == 'a' and self.in_social:
            self.social_links.append(a.get('href'))
        if tag == 'p' and 'feature-label' in classes:
            self.in_feature_label = True
        if tag == 'div':
            self.div_depth += 1
            if 'action-group' in classes:
                self.action_groups.append({'depth': self.div_depth, 'buttons': []})
        if tag == 'a' and 'button' in classes and self.action_groups:
            self.action_groups[-1]['buttons'].append('button-primary' in classes)
        if 'button-primary' in classes and not self.action_groups:
            errors.append(f'primary action must belong to an ordered group: {self.filename}')
        if 'data-search-open' in a:
            self.search_trigger = True
        if tag == 'meta' and a.get('data-pagefind-meta') in ('section[content]', 'date[content]'):
            self.search_metadata[a['data-pagefind-meta'].split('[')[0]] = a.get('content')
        if tag == 'footer':
            self.in_footer = True
        if tag == 'nav' and a.get('id') == 'primary-nav':
            self.in_primary_nav = True
        if tag == 'a' and self.in_primary_nav:
            self.navigation_links.append(a.get('href'))
        if 'attention-fallback' in classes and (a.get('role') != 'img' or not a.get('aria-label') or 'hidden' in a):
            errors.append(f'Altmetric needs an accessible, initially visible empty ring: {self.filename}')
        if tag == 'a' and a.get('href', '').endswith(cv_path) and 'download' in a:
            errors.append(f'CV should open in the browser: {self.filename}')
        if 'altmetric-embed' in a.get('class', '').split():
            self.badges.append(a.get('data-doi'))
        if 'id' in a:
            if a['id'] in self.ids:
                errors.append(f'duplicate id: {self.filename} #{a["id"]}')
            self.ids.add(a['id'])
            self.ordered_ids.append(a['id'])
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'main':
            self.main += 1
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href', '')
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            errors.append(f'unexpected redirect: {self.filename}')
        for key in ('href', 'src'):
            if a.get(key):
                self.links.append(a[key])
        if 'srcset' in a:
            self.links.extend(x.strip().split()[0] for x in a['srcset'].split(','))
        if tag == 'img' and 'alt' not in a:
            errors.append(f'image missing alt: {self.filename}')
        if tag == 'button' and not a.get('aria-label'):
            errors.append(f'button missing accessible name: {self.filename}')

    def handle_endtag(self, tag):
        if tag == 'h4':
            self.in_question_subheading = False
        if tag == 'article':
            self.active_question = ''
            self.active_publication = ''
        if tag == 'ul':
            self.in_social = False
        if tag == 'p':
            self.in_feature_label = False
            self.in_publication_label = False
        if tag == 'div':
            if self.action_groups and self.action_groups[-1]['depth'] == self.div_depth:
                buttons = self.action_groups.pop()['buttons']
                if not buttons or not buttons[0] or sum(buttons) != 1:
                    errors.append(f'action group must start with its sole primary button: {self.filename}')
            self.div_depth -= 1
        if tag == 'footer':
            self.in_footer = False
        if tag == 'nav':
            self.in_primary_nav = False

    def handle_data(self, text):
        if self.in_publication_label and text.strip():
            self.publication_labels[self.active_publication].append(text.strip())
        if self.in_question_subheading and text.strip():
            self.question_subheadings[self.active_question].append(text.strip())
        if self.in_feature_label and text.strip():
            self.feature_labels.append(text.strip())
        if self.in_footer and text.strip():
            self.footer_text.append(text.strip())


def target_for(path):
    # A project site URL such as /website-preview/about/ maps to public/about/.
    dest = root / unquote(path.removeprefix(base_path)).lstrip('/')
    return dest / 'index.html' if dest.is_dir() else dest


if not root.is_dir():
    sys.exit(f'Build directory not found: {root}')
documents = {}
for path in root.rglob('*.html'):
    doc = Document()
    doc.filename = path.relative_to(root)
    doc.feed(path.read_text())
    documents[path] = doc
    if 'main' in doc.ids:
        if doc.h1 != 1 or doc.main != 1 or not doc.lang or not doc.canonical:
            errors.append(f'invalid page landmarks/metadata: {doc.filename}')
        if ' '.join(doc.footer_text) != f'© {datetime.now(timezone.utc).year} {profile["en"]["name"]}':
            errors.append(f'footer must contain only the copyright: {doc.filename}')
        if not doc.search_trigger or 'search-dialog' not in doc.ids:
            errors.append(f'missing navigation search: {doc.filename}')
        if doc.filename.name != '404.html' and not doc.search_metadata.get('section'):
            errors.append(f'missing search section metadata: {doc.filename}')

home = documents.get(root / 'index.html')
if home and home.canonical:
    base_path = urlsplit(home.canonical).path.rstrip('/') + '/'
    site_host = urlsplit(home.canonical).netloc

for path, doc in documents.items():
    current = base_path + path.relative_to(root).as_posix()
    if 'main' in doc.ids:
        prefix = base_path + ('zh/' if doc.lang.lower().startswith('zh') else '')
        expected_navigation = [prefix + section + '/' for section in
                               sections]
        if doc.navigation_links != expected_navigation:
            errors.append(f'{doc.filename}: navigation language or base path is incorrect')
    for link in doc.links:
        parsed = urlsplit(link)
        if (parsed.scheme or parsed.netloc) and parsed.netloc != site_host:
            continue
        resolved = urlsplit(urljoin(current, link))
        if not resolved.path.startswith(base_path):
            errors.append(f'{doc.filename}: internal link escapes the site base path: {link}')
            continue
        target = target_for(resolved.path)
        if not target.is_file():
            errors.append(f'{doc.filename}: broken internal link {link}')
        elif resolved.fragment and target in documents and unquote(resolved.fragment) not in documents[target].ids:
            errors.append(f'{doc.filename}: unknown fragment {link}')

# HTML-only entities in descriptions are invalid XML even when HTML pages build.
for path in root.rglob('*.xml'):
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f'invalid XML: {path.relative_to(root)}: {exc}')

for lang in ('', 'zh/'):
    for section in sections:
        if not (root / lang / section / 'index.html').is_file():
            errors.append(f'missing section: /{lang}{section}/')
for name in ('pagefind-ui.js', 'pagefind-ui.css', 'pagefind.js'):
    if not (root / 'pagefind' / name).is_file():
        errors.append(f'missing search asset: {name}')

# Compare rendered lists against source controls, including homepage selection.
def display_order(record):
    priority = record['display']['order']
    return (priority == 0, priority, -int(str(record['date']).replace('-', '')), record['id'])


groups = {'publications': 'publications', 'data': 'resources',
          'presentations': 'presentations', 'news': 'news'}
for lang in ('', 'zh/'):
    home_doc = documents.get(root / lang / 'index.html')
    language = 'zh' if lang else 'en'
    about_doc = documents.get(root / lang / 'about/index.html')
    expected_social = [link['url'] for link in profile['links'] if language in link['languages']]
    if about_doc and about_doc.social_links != expected_social:
        errors.append(f'{lang}about: social links or order differ from the shared language controls')
    if about_doc and '/images/' + str(Path(profile['portrait']).with_suffix('')) + '_' not in about_doc.share_image:
        errors.append(f'{lang}about: sharing image must use the profile portrait')
    expected_home = set()
    expected_home_sequence = []
    translations = yaml.safe_load((source / f'i18n/{language}.yaml').read_text())
    expected_labels = []
    for section, group in groups.items():
        records = [normalize(group, yaml.safe_load(p.read_text())) for p in (source / 'data' / group).glob('*.yaml')]
        visible = [r for r in records if r['display']['visible']]
        hero = yaml.safe_load((source / 'data/home.yaml').read_text())['hero']['image']
        for record in records:
            detail = documents.get(root / lang / section / record['id'].lower() / 'index.html')
            image = record['image'] if record['display']['image'] else hero
            expected_image = '/images/' + (image if Path(image).suffix.lower() in ('.svg', '.gif') else str(Path(image).with_suffix('')) + '_')
            if detail and expected_image not in detail.share_image:
                errors.append(f'{lang}{section}/{record["id"]}: sharing image differs from shared image controls')
        expected_labels.extend([translations['highlights']['other'] + ' · ' + translations[section]['other']]
                               * sum(r['display']['home'] for r in visible))
        doc = documents.get(root / lang / section / 'index.html')
        if not doc:
            continue
        if section == 'publications':
            expected = {'paper-' + r['id'] for r in visible}
            actual = {i for i in doc.ids if i.startswith('paper-')}
            ordered = sorted(visible, key=lambda r: (-record_year(r), not r['display']['featured'], *display_order(r)))
            if [i for i in doc.ordered_ids if i.startswith('paper-')] != ['paper-' + r['id'] for r in ordered]:
                errors.append(f'{lang}{section}: year, featured or within-group order differs from source')
            selected = {r['id'] for r in visible if r['display']['home']}
            selected_sequence = ['home-' + i.removeprefix('paper-') for i in doc.ordered_ids
                                 if i.startswith('paper-') and i.removeprefix('paper-') in selected]
            if home_doc and [i for i in home_doc.ordered_ids if i.startswith('home-')] != selected_sequence:
                errors.append(f'{lang}home: publication highlights must preserve their section sequence')
            labels = {'paper-' + r['id']: [translations['featured']['other'] + ' · ' + translations[section]['other']]
                      for r in visible if r['display']['featured']}
            if doc.publication_labels != labels:
                errors.append(f'{lang}{section}: featured labels differ from source')
            expected_badges = {r['doi'] for r in visible if r['display']['attention'] and r['doi']}
            if set(doc.badges) != expected_badges:
                errors.append(f'{lang}{section}: Altmetric controls do not match source')
        else:
            ordered = sorted(visible, key=display_order)
            expected = {('feature-' if r['display']['featured'] else 'record-') + r['id'] for r in visible}
            actual = {i for i in doc.ids if i.startswith(('feature-', 'record-'))}
        if actual != expected:
            errors.append(f'{lang}{section}: visible/featured controls do not match source')
        if section in ('publications', 'data', 'presentations', 'news'):
            grouped = visible if section == 'publications' else [r for r in visible if not r['display']['featured']]
            expected_years = {'year-' + str(record_year(r)) for r in grouped}
            actual_years = {i for i in doc.ids if i.startswith('year-')}
            if expected_years != actual_years:
                errors.append(f'{lang}{section}: year groups do not match source')
        if section == 'publications':
            for record in records:
                citation = root / lang / section / record['id'].lower() / 'cite.bib'
                if not citation.is_file():
                    errors.append(f'{record["id"]}: missing generated citation')
                    continue
                text = citation.read_text()
                for value in (record['title'], ' and '.join(record['authors']), str(record_year(record)), record['doi']):
                    escaped = ''.join('\\' + c if c in '&%$#_{}' else c for c in value)
                    if value not in text and escaped not in text:
                        errors.append(f'{record["id"]}: citation differs from shared facts')
        expected_home.update(('home-' if section == 'publications' else 'record-') + r['id']
                             for r in visible if r['display']['home'])
        expected_home_sequence.extend(('home-' if section == 'publications' else 'record-') + r['id']
                                      for r in ordered if r['display']['home'])
    if home_doc:
        if home_doc.feature_labels != expected_labels:
            errors.append(f'{lang}home: highlights labels or section order differ from source')
        actual_home = {i for i in home_doc.ids if i.startswith(('home-', 'record-'))}
        if actual_home != expected_home:
            errors.append(f'{lang}home: homepage controls do not match source')
        if [i for i in home_doc.ordered_ids if i.startswith(('home-', 'record-'))] != expected_home_sequence:
            errors.append(f'{lang}home: highlight sequence differs from the shared display rules')
# Research owns references; SQ navigation must not leak into the other sections.
questions = yaml.safe_load((source / 'data/questions.yaml').read_text())
framework = yaml.safe_load((source / 'data/framework.yaml').read_text()) if research_layout['framework_enabled'] else {'stages': []}
for lang in ('', 'zh/'):
    research = documents.get(root / lang / 'research/index.html')
    if not research:
        continue
    if not question_ids <= research.ids:
        errors.append(f'{lang}research: missing question anchors')
    def resource_links(section, group, ids):
        result = set()
        for ident in ids:
            record = normalize(group, yaml.safe_load((source / 'data' / group / (ident + '.yaml')).read_text()))
            if record['display']['visible']:
                result.add(base_path + lang + section + '/' + ident.lower() + '/')
        return result
    labels = research_layout['paragraph_labels']
    translations = yaml.safe_load((source / f'i18n/{"zh" if lang else "en"}.yaml').read_text())
    for q in questions:
        expected = resource_links('publications', 'publications', q['paper_ids'])
        expected |= resource_links('data', 'resources', q['data_ids'])
        if set(research.question_resources.get(q['id'], [])) != expected:
            errors.append(f'{lang}research/{q["id"]}: references differ from Research selections')
        if research.question_paragraphs.get(q['id']) != len(labels):
            errors.append(f'{lang}research/{q["id"]}: expected three narrative paragraphs')
        if research.question_subheadings.get(q['id']) != [translations[key]['other'] for key in labels]:
            errors.append(f'{lang}research/{q["id"]}: paragraph subheadings differ from shared translations')
    term_papers = [t['paper_id'] for stage in framework['stages'] for t in stage['terms'] if t['paper_id']] if research_layout['framework_enabled'] else []
    visible_papers = resource_links('publications', 'publications', term_papers)
    expected_papers = [base_path + lang + 'publications/' + ident.lower() + '/' for ident in term_papers]
    if research.framework_papers != [link for link in expected_papers if link in visible_papers]:
        errors.append(f'{lang}research: framework paper links differ from term references')
for path, doc in documents.items():
    if path not in (root / 'research/index.html', root / 'zh/research/index.html'):
        if any(urlsplit(link).path.rstrip('/').endswith('/research') and urlsplit(link).fragment in question_ids for link in doc.links):
            errors.append(f'{doc.filename}: SQ navigation belongs only in Research')
if errors:
    print('\n'.join(sorted(set(errors))), file=sys.stderr)
    sys.exit(1)
print(f'Links OK: {len(documents)} HTML files; internal URLs, fragments, images, citations, and section routes resolve.')
