"""Content contract shared by source/output checks and the record generator."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.YAMLError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path):
    return yaml.load(Path(path).read_text(encoding='utf-8'), Loader=UniqueLoader)


SCHEMA = read_yaml(ROOT / 'data/content_schema.yaml')
GROUPS = {spec['section']: group for group, spec in SCHEMA['groups'].items()}


def normalize(group, raw):
    record = deepcopy(SCHEMA['common']['defaults'])
    record.update(deepcopy(SCHEMA['groups'][group]['defaults']))
    record.update(deepcopy(raw))
    if group == 'publications' and record['type'] == 'preprint' and 'status' not in raw:
        record['status'] = 'preprint'
    display = deepcopy(SCHEMA['display']['common'])
    display.update(SCHEMA['display'].get(group, {}))
    display.update(raw.get('display', {}) if isinstance(raw.get('display', {}), dict) else {})
    record['display'] = display
    return record


def record_year(record):
    return record.get('year') or int(str(record['date'])[:4])


def validate_records(root=ROOT):
    errors, records = [], {g: {} for g in SCHEMA['groups']}
    def check(ok, origin, message):
        if not ok:
            errors.append(f'{origin}: {message}')
    def valid_date(value):
        try:
            return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(value))) and bool(date.fromisoformat(str(value)))
        except (ValueError, TypeError):
            return False
    def url(value, origin, optional=False):
        if optional and not value:
            return
        try:
            parsed = urlsplit(str(value))
        except ValueError:
            check(False, origin, f'invalid URL: {value}')
            return
        check((parsed.scheme == 'https' and bool(parsed.netloc)) or
              (parsed.scheme == 'mailto' and bool(parsed.path)) or
              (str(value).startswith('/') and not parsed.netloc), origin,
              f'expected HTTPS, mailto, or a site-relative URL: {value}')
        if str(value).startswith('/') and not parsed.netloc:
            dest = root / 'static' / unquote(parsed.path).lstrip('/')
            # Site pages and anchors are checked after building, not mistaken for downloads.
            if parsed.path.startswith(('/uploads/', '/images/')):
                check(dest.is_file(), origin, f'missing local file {parsed.path}')
    types = {
        'string': lambda v: isinstance(v, str),
        'scalar': lambda v: isinstance(v, (str, int, float)) and not isinstance(v, bool),
        'integer': lambda v: type(v) is int,
        'date': valid_date,
        'object': lambda v: isinstance(v, dict),
        'list': lambda v: isinstance(v, list),
        'strings': lambda v: isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v),
        'ids': lambda v: isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v) and len(v) == len(set(v)),
        'bilingual': lambda v: isinstance(v, dict) and set(v) == {'en', 'zh'} and all(isinstance(x, str) for x in v.values()),
    }
    for group, spec in SCHEMA['groups'].items():
        paths = sorted((root / 'data' / group).glob('*.yaml'))
        folded = {}
        for path in paths:
            origin = str(path.relative_to(root))
            try:
                raw = read_yaml(path)
            except (OSError, yaml.YAMLError) as exc:
                errors.append(f'{origin}: {exc}')
                continue
            if not isinstance(raw, dict):
                errors.append(f'{origin}: expected a record object')
                continue
            before = len(errors)
            fields = SCHEMA['common']['fields'] | spec['fields']
            check(raw.get('id') == path.stem, origin, 'id must match filename')
            check(bool(re.fullmatch(r'[A-Za-z0-9_-]+', str(raw.get('id', '')))), origin, 'id must be a stable path-safe key')
            check(path.stem.lower() not in folded, origin, f'output path collision with {folded.get(path.stem.lower())}')
            folded[path.stem.lower()] = path.stem
            for key in raw.keys() - fields.keys():
                check(False, origin, f'unknown field {key}; see data/content_schema.yaml')
            for key in SCHEMA['common']['required'] + spec['required']:
                check(bool(raw.get(key)), origin, f'missing required field {key}')
            for key, value in raw.items():
                if key in fields:
                    check(types[fields[key]](value), origin, f'{key} must be {fields[key]}')
            for key, values in (SCHEMA['common'].get('enums', {}) | spec.get('enums', {})).items():
                if key in raw:
                    check(raw[key] in values, origin, f'{key}: allowed values are {values}')
            if len(errors) != before:
                continue  # Avoid secondary exceptions from invalid types.
            r = normalize(group, raw)
            records[group][path.stem] = r
            display = raw.get('display', {})
            allowed = SCHEMA['display']['common'] | SCHEMA['display'].get(group, {})
            for key in display.keys() - allowed.keys():
                check(False, origin, f'unknown display field {key}')
            for key, value in display.items():
                ordered = key == 'order'
                check(type(value) is int and value >= 0 if ordered else type(value) is bool,
                      origin, f'display.{key} must be a nonnegative integer' if ordered else f'display.{key} must be true/false')
            check(not r['display']['home'] or r['display']['featured'], origin,
                  'display.home: true requires display.featured: true')
            if r['date_precision'] in ('month', 'year'):
                suffix = '-01' if r['date_precision'] == 'month' else '-01-01'
                check(str(r['date']).endswith(suffix), origin, f'{r["date_precision"]} dates use {suffix} for sorting only')
            for key in ('end_date', 'updated'):
                if key in r:
                    check(str(r[key]) >= str(r['date']), origin, f'{key} cannot precede date')
                    if key == 'end_date' and r['date_precision'] != 'day':
                        suffix = '-01' if r['date_precision'] == 'month' else '-01-01'
                        check(str(r[key]).endswith(suffix), origin, f'end_date must match {r["date_precision"]} precision')
            if r['image']:
                image = root / 'assets/images' / r['image']
                check(image.is_file(), origin, f'missing image {r["image"]}')
                check(image.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'), origin, 'supported images: PNG, JPEG, WebP, GIF, SVG')
            check(not r['display']['image'] or bool(r['image']), origin, 'image enabled without an image')
            if group in ('publications', 'resources'):
                check(r['image_fit'] == 'contain', origin, 'scientific figures and interfaces must not be cropped')
            for i, link in enumerate(r['links']):
                loc = f'{origin} links[{i}]'
                if not isinstance(link, dict):
                    check(False, loc, 'expected an object')
                    continue
                check(set(link) <= {'label', 'url', 'name', 'download'} and {'label', 'url'} <= set(link), loc, 'use label/url with optional bilingual name and download')
                check(isinstance(link.get('label'), str) and bool(link['label']), loc, 'label needs a translation key')
                check(isinstance(link.get('url'), str), loc, 'url must be a string')
                url(link.get('url', ''), loc)
                if 'name' in link:
                    check(types['bilingual'](link['name']) and all(link['name'].values()), loc, 'name needs nonempty en/zh text')
                if 'download' in link:
                    check(type(link['download']) is bool, loc, 'download must be true/false')
            if group == 'publications':
                if r.get('year') is not None:
                    check(1900 <= r['year'] <= 2100, origin, 'year must be a valid formal publication year')
                if r['status'] in ('published', 'online_first'):
                    check(bool(r.get('year')), origin, 'published/online_first work needs its publication year')
                    venue = {'article': 'journal', 'conference': 'booktitle', 'chapter': 'booktitle', 'report': 'institution'}.get(r['type'])
                    if venue:
                        check(bool(r.get(venue)), origin, f'{r["type"]} needs {venue} when published')
                check(r['type'] == 'preprint' if r['status'] == 'preprint' else r['type'] != 'preprint', origin, 'preprint type and status must agree')
                check(not (r['pages'] and r['article_number']), origin, 'use pages or article_number, not both')
                url(r.get('url', ''), f'{origin} url', optional=True)
                roles = r['author_roles']
                check(set(roles) <= {'equal_contribution', 'corresponding'}, origin, 'author_roles supports equal_contribution/corresponding')
                for role, names in roles.items():
                    check(types['ids'](names) and all(n in r['authors'] for n in names), origin, f'author_roles.{role} must list exact authors')
            if group in ('publications', 'resources') and r.get('doi'):
                check(bool(re.fullmatch(r'10\.\d{4,9}/\S+', r['doi'])), origin, 'doi must be a bare DOI')
            if group == 'resources' and r['citation']:
                c = r['citation']
                check(set(c) <= {'title', 'authors', 'year', 'publisher', 'doi', 'url'} and {'title', 'authors', 'year'} <= set(c), origin, 'citation needs title/authors/year, optional publisher/doi/url')
                check(isinstance(c.get('title'), str) and bool(c['title']) and types['strings'](c.get('authors')) and bool(c.get('authors')) and type(c.get('year')) is int, origin, 'citation title/authors/year have invalid types')
                for key in ('publisher', 'doi', 'url'):
                    if key in c:
                        check(isinstance(c[key], str), origin, f'citation.{key} must be a string')
                if c.get('doi'):
                    check(bool(re.fullmatch(r'10\.\d{4,9}/\S+', str(c['doi']))), origin, 'citation.doi must be bare')
                    check(not r['doi'] or r['doi'] == c['doi'], origin, 'resource DOI and citation DOI disagree')
                url(c.get('url', ''), f'{origin} citation.url', optional=True)
            if group == 'presentations':
                url(r['event_url'], f'{origin} event_url', optional=True)
                if r['role'] == 'keynote':
                    check(r['kind'] in ('oral', 'seminar'), origin, 'keynote role requires an oral/seminar presentation')
                if r['kind'] == 'other':
                    check(types['bilingual'](r.get('kind_label')) and all(r.get('kind_label', {}).values()), origin, 'kind: other requires nonempty bilingual kind_label')
                for key in ('event_label', 'location_label'):
                    if key in r:
                        check(all(r[key].values()), origin, f'{key} needs nonempty en/zh strings')
        visible = [r for r in records[group].values() if r['display']['visible']]
        if group != 'publications':
            check(sum(bool(r['display']['featured']) for r in visible) <= 1, f'data/{group}', 'at most one visible featured record is allowed')
            check(sum(bool(r['display']['home']) for r in visible) <= 1, f'data/{group}', 'at most one visible homepage selection is allowed')
    if errors:
        return records, errors
    for group, values in records.items():
        for ident, r in values.items():
            for field, target in [('paper_ids', 'publications'), ('presentation_ids', 'presentations'), ('related_version_ids', group)]:
                for linked in r.get(field, []):
                    check(linked in records[target], f'{group}/{ident}', f'{field}: unknown ID {linked}')
                    if field == 'related_version_ids':
                        check(linked != ident, f'{group}/{ident}', 'a version cannot reference itself')
    return records, errors
