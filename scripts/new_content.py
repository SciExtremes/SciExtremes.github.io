#!/usr/bin/env python3
"""Create a shared record and its EN/ZH pages without overwriting existing content."""
import argparse
from datetime import date
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import yaml
from content_model import GROUPS, ROOT, SCHEMA, validate_records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('section', choices=GROUPS)
    p.add_argument('id', help='stable ID; it does not change when dates or titles change')
    p.add_argument('--date', required=True, help='YYYY-MM-DD; use -01/-01-01 for month/year precision')
    p.add_argument('--precision', choices=SCHEMA['common']['enums']['date_precision'], default='day')
    p.add_argument('--title-en', required=True)
    p.add_argument('--title-zh', required=True)
    p.add_argument('--author', action='append', default=[], help='repeat for each formal author')
    p.add_argument('--type', choices=SCHEMA['groups']['publications']['enums']['type'], default='article')
    p.add_argument('--status', choices=SCHEMA['groups']['publications']['enums']['status'])
    p.add_argument('--venue', help='journal/booktitle/repository/institution, depending on type')
    p.add_argument('--event')
    p.add_argument('--kind', choices=SCHEMA['groups']['presentations']['enums']['kind'], default='oral')
    p.add_argument('--name', help='shared formal resource name')
    a = p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', a.id):
        p.error('ID must contain only letters, digits, underscores or hyphens')
    if not a.title_en.strip() or not a.title_zh.strip():
        p.error('both titles must be nonempty')
    group = GROUPS[a.section]
    r = {'id': a.id, 'date': a.date, 'date_precision': a.precision, 'display': {'visible': False}}
    if a.section == 'publications':
        if not a.author:
            p.error('publications need one or more --author arguments')
        r.update(title=a.title_en, authors=a.author, type=a.type,
                 status=a.status or ('preprint' if a.type == 'preprint' else 'published'))
        if r['status'] in ('published', 'online_first'):
            try:
                r['year'] = date.fromisoformat(a.date).year
            except ValueError:
                p.error('invalid date')
        if a.venue:
            r[{'article': 'journal', 'conference': 'booktitle', 'preprint': 'repository', 'chapter': 'booktitle', 'report': 'institution'}[a.type]] = a.venue
    elif a.section == 'presentations':
        if not a.event:
            p.error('presentations need --event')
        if a.kind == 'other':
            p.error('create with a standard kind, then set other and its bilingual kind_label')
        r.update(event=a.event, kind=a.kind)
    elif a.section == 'data':
        if not a.name:
            p.error('data needs --name for its shared formal resource name')
        r['name'] = a.name
    paths = [ROOT / 'data' / group / f'{a.id}.yaml']
    paths += [ROOT / 'content' / lang / a.section / a.id / 'index.md' for lang in ('en', 'zh')]
    for parent in (ROOT / 'data' / group, ROOT / 'content/en' / a.section, ROOT / 'content/zh' / a.section):
        for existing in parent.iterdir():
            key = existing.stem if existing.is_file() else existing.name
            if key.lower() == a.id.lower():
                p.error(f'ID/output path already exists: {existing.relative_to(ROOT)}')
    with TemporaryDirectory() as temp:
        fixture = Path(temp)
        target = fixture / 'data' / group / f'{a.id}.yaml'
        target.parent.mkdir(parents=True)
        target.write_text(yaml.safe_dump(r, allow_unicode=True, sort_keys=False))
        _, errors = validate_records(fixture)
        if errors:
            p.error('\n'.join(errors))
    texts = [yaml.safe_dump(r, allow_unicode=True, sort_keys=False)]
    for lang, title in (('en', a.title_en), ('zh', a.title_zh)):
        meta = {'record_id': a.id}
        if a.section == 'publications':
            if lang == 'zh':
                meta['translated_title'] = title
        else:
            meta['title'] = title
        meta['summary'] = ''
        texts.append('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' +
                     ('Add the public abstract or description here.\n' if lang == 'en' else '在此填写公开摘要或介绍。\n'))
    for path, text in zip(paths, texts):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as f:
            f.write(text)
    print('\n'.join(str(path.relative_to(ROOT)) for path in paths))
    print('Created with display.visible: false. Complete both pages, then choose visibility and run checks.')


if __name__ == '__main__':
    main()
