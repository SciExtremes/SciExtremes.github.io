#!/usr/bin/env python3
"""Check bilingual document pairs, shared technical examples and local links."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []
FENCES = re.compile(r'(?ms)^```([^\n]*)\n(.*?)^```[ \t]*\n?')


def prose(text):
    return FENCES.sub('', text)


def anchors(path):
    result, used = set(), {}
    text = prose(path.read_text())
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', re.sub(r'[`*_]', '', heading).lower()).replace(' ', '-')
        count = used.get(slug, 0)
        used[slug] = count + 1
        result.add(slug if count == 0 else f'{slug}-{count}')
    result.update(re.findall(r'\bid=["\']([^"\']+)', text))
    return result


def links(text):
    text = re.sub(r'`[^`\n]+`', '', prose(text))
    return re.findall(r'\[[^]]*\]\(([^\s)]+)', text) + re.findall(r'^\s*\[[^]]+\]:\s*(\S+)', text, re.M)


def technical_terms(text):
    return set(re.findall(r'`([^`\n]+)`', prose(text)))


def document_language(path):
    for language, readme in (('zh', 'README.md'), ('en', 'README.en.md')):
        if path == ROOT / readme or path.is_relative_to(ROOT / 'docs' / language):
            return language
    return None


zh = {p.relative_to(ROOT / 'docs/zh'): p for p in (ROOT / 'docs/zh').rglob('*.md')}
en = {p.relative_to(ROOT / 'docs/en'): p for p in (ROOT / 'docs/en').rglob('*.md')}
if not zh or zh.keys() != en.keys():
    errors.append(f'docs: Chinese/English document paths differ: {sorted(set(zh) ^ set(en))}')
pairs = [(ROOT / 'README.md', ROOT / 'README.en.md')]
pairs.extend((zh[key], en[key]) for key in sorted(zh.keys() & en.keys()))
counterparts = {source: target for chinese, english in pairs
                for source, target in ((chinese, english), (english, chinese))}
for chinese, english in pairs:
    if not chinese.is_file() or not english.is_file():
        errors.append(f'docs: missing language counterpart for {chinese.name}/{english.name}')
        continue
    ctext, etext = chinese.read_text(), english.read_text()
    chead = [len(h) for h in re.findall(r'^(#{1,6})\s+', prose(ctext), re.M)]
    ehead = [len(h) for h in re.findall(r'^(#{1,6})\s+', prose(etext), re.M)]
    if chead != ehead:
        errors.append(f'{chinese.relative_to(ROOT)}: section structure differs from English counterpart')
    cblocks = [(language.strip(), body.rstrip()) for language, body in FENCES.findall(ctext)]
    eblocks = [(language.strip(), body.rstrip()) for language, body in FENCES.findall(etext)]
    if cblocks != eblocks:
        errors.append(f'{chinese.relative_to(ROOT)}: code examples differ from English counterpart')
    cterms, eterms = technical_terms(ctext), technical_terms(etext)
    if cterms != eterms:
        errors.append(f'{chinese.relative_to(ROOT)}: technical terms differ; Chinese-only={sorted(cterms-eterms)}, English-only={sorted(eterms-cterms)}')
    for source, target, text in ((chinese, english, ctext),(english, chinese, etext)):
        if not any((source.parent / unquote(urlsplit(ref).path)).resolve() == target.resolve() for ref in links(text) if not urlsplit(ref).scheme):
            errors.append(f'{source.relative_to(ROOT)}: missing link to its language counterpart')

paths = sorted(set([*ROOT.glob('README*.md'), ROOT / 'LICENSE.md', *(ROOT / 'docs').rglob('*.md')]))
for path in paths:
    if not path.is_file():
        errors.append(f'missing document: {path.relative_to(ROOT)}')
        continue
    for ref in links(path.read_text()):
        try:
            parsed = urlsplit(ref.strip('<>'))
        except ValueError:
            errors.append(f'{path.relative_to(ROOT)}: invalid link {ref}')
            continue
        if parsed.scheme or parsed.netloc:
            continue
        dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not dest.exists():
            errors.append(f'{path.relative_to(ROOT)}: missing local target {ref}')
        elif parsed.fragment and dest.suffix.lower() == '.md' and unquote(parsed.fragment) not in anchors(dest):
            errors.append(f'{path.relative_to(ROOT)}: missing Markdown anchor {ref}')
        elif source_language := document_language(path):
            target_language = document_language(dest)
            if target_language and target_language != source_language and dest != counterparts.get(path):
                errors.append(f'{path.relative_to(ROOT)}: local navigation changes document language: {ref}')
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Documentation OK: {len(pairs)} language pairs; sections, technical examples, language navigation and local links agree.')
