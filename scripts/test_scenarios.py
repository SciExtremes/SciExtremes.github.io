#!/usr/bin/env python3
"""Build supported content scenarios in a disposable clone; production content is untouched."""
import base64
import os
import re
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import yaml
from content_model import ROOT


def run(command, cwd, env=None):
    subprocess.run(command, cwd=cwd, env=env, check=True)


with TemporaryDirectory(prefix='academic-site-test-') as temp:
    repo = Path(temp) / 'site'
    def ignored(directory, names):
        excluded = {'__pycache__', '.git', '.hugo_build.lock'}
        if Path(directory) == ROOT:
            excluded |= {'node_modules', 'public', 'resources'}
        return set(names) & excluded
    shutil.copytree(ROOT, repo, ignore=ignored)
    (repo / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
    def record(section, data, body='Public test description.', title=None):
        group = 'resources' if section == 'data' else section
        path = repo / 'data' / group / (data['id'] + '.yaml')
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
        for lang in ('en', 'zh'):
            content = repo / 'content' / lang / section / data['id'] / 'index.md'
            content.parent.mkdir(parents=True)
            meta = {'record_id': data['id'], 'summary': 'Content scenarios fixture.'}
            if section != 'publications':
                meta['title'] = title or 'Content scenarios ' + data['id']
            content.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' + body + '\n')
    title = 'Example study & methods: ' + ('LongScientificTerminology' * 5) + ' {case study}'
    variants = [('article','journal'),('conference','booktitle'),('chapter','booktitle'),('report','institution'),('preprint','repository')]
    for kind, venue in variants:
        r = dict(id='fixture-' + kind, date='2027-01-01', date_precision='year', title=title, authors=['Example Researcher', 'Author With An Extended Formal Name', 'Álvaro Researcher'], type=kind, **{venue:'Example venue'})
        if kind != 'preprint':
            r['year'] = 2027
        if kind == 'article':
            r.update(article_number='e12345', author_roles={'equal_contribution':['Example Researcher'], 'corresponding':['Example Researcher']})
        record('publications',r)
    record('publications',dict(id='fixture-accepted',date='2027-02-01',title='Accepted without DOI or formal year',authors=['Example Researcher'],status='accepted',display={'attention':True},related_version_ids=['fixture-preprint']))
    record('publications',dict(id='fixture-online',date='2027-03-01',title='Online first without volume and pages',authors=['Example Researcher'],journal='Future journal',year=2027,status='online_first',doi='10.12345/fixture-online',display={'attention':False}))
    # Homepage selections retain the section's shared year/feature/priority sequence.
    for ident, day, year, display in (
        ('selected-a', '2027-01-02', 2027, {'featured': True, 'home': True, 'order': 1}),
        ('selected-b', '2027-02-02', 2027, {'featured': True, 'home': True, 'order': 5}),
        ('selected-tie-a', '2027-08-02', 2027, {'featured': True, 'home': True, 'order': 5}),
        ('selected-tie-b', '2027-08-02', 2027, {'featured': True, 'home': True, 'order': 5}),
        ('section-only', '2027-09-02', 2027, {'featured': True, 'order': 2}),
        ('selected-auto', '2027-05-02', 2027, {'featured': True, 'home': True}),
        ('regular-priority', '2027-12-02', 2027, {'order': 1}),
        ('formal-year', '2026-01-02', 2028, {'featured': True, 'home': True, 'order': 50}),
        ('hidden-feature', '2029-01-02', 2029, {'visible': False, 'featured': True, 'home': True, 'order': 1}),
    ):
        record('publications', dict(id='fixture-' + ident, date=day, year=year,
               title='Example editorial selection ' + ident, authors=['Example Researcher'],
               journal='Example journal', display=display))
    record('publications', dict(id='fixture-selected-accepted', date='2028-01-03',
           title='Selected accepted study without a formal year', authors=['Example Researcher'],
           status='accepted', display={'featured': True, 'home': True}))
    record('presentations',dict(id='fixture-oral',date='2027-05-02',end_date='2027-05-04',event='International Meeting With A Long Official Name',kind='oral',event_type='seminar',role='invited',participation='online',paper_ids=['fixture-accepted']))
    record('presentations',dict(id='fixture-keynote',date='2027-01-01',event='Conference',kind='oral',role='keynote',event_type='conference',event_label={'en':'Conference','zh':'学术会议'},location_label={'en':'Venue','zh':'会场'}))
    record('presentations',dict(id='fixture-other',date='2027-01-01',event='Discussion',kind='other',kind_label={'en':'Panel discussion','zh':'专题讨论'}))
    (repo / 'assets/images/fixture-vector.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200"><rect width="400" height="200" fill="#dae9f8"/><text x="20" y="100">Scientific vector fixture</text></svg>')
    # A tiny GIF tests original-file preservation rather than raster conversion.
    (repo / 'assets/images/fixture-animation.gif').write_bytes(base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'))
    (repo / 'static/uploads/fixture-note.txt').write_text('Public supplementary attachment fixture.\n')
    body = '![Vector description](/images/fixture-vector.svg)\n\n{{< figure src="/images/fixture-vector.svg" alt="Vector alternative" caption="Supplementary scientific figure." >}}\n\n![Original GIF](/images/fixture-animation.gif)\n\n[Supplement](/uploads/fixture-note.txt?download=1#note)'
    for ident in ('dataset','code'):
        record('data',dict(id='fixture-'+ident,date='2027-01-01',name='Example '+ident,resource_type=ident,version='2.0',license='CC BY 4.0',updated='2027-02-01',paper_ids=['fixture-article'],links=[{'label':'accessData' if ident=='dataset' else 'Code','url':'https://resources.example.org/'+ident,'name':{'en':'Historical resource','zh':'历史资源'}},{'label':'documentation','url':'https://resources.example.org/docs'}],citation={'title':'Example resource','authors':['Example Researcher'],'year':2027}),body=body)
    record('news',dict(id='fixture-tie-a',date='2027-01-01',presentation_ids=['fixture-oral']))
    record('news',dict(id='fixture-tie-b',date='2027-01-01'))
    for base in ('https://example.org/', 'https://example.org/academic-site/'):
        env = os.environ | {'HUGO_BASEURL':base}
        run(['python3','scripts/validate_content.py'],repo,env)
        run(['npm','run','build'],repo,env)
        run(['python3','scripts/check_links.py','public'],repo,env)
        output = repo / 'public'
        accepted = (output / 'publications/fixture-accepted/index.html').read_text()
        assert 'https://doi.org/' not in accepted and 'altmetric-embed' not in accepted
        assert 'citation_title' in accepted and 'Accepted' in accepted
        for kind, _ in variants:
            bib = (output / f'publications/fixture-{kind}/cite.bib').read_text()
            assert bib.startswith('@'+{'article':'article','conference':'inproceedings','chapter':'incollection','report':'techreport','preprint':'misc'}[kind]+'{')
            assert '\\&' in bib and '\\{case study\\}' in bib
        talk = (output / 'presentations/fixture-oral/index.html').read_text()
        assert 'Invited Seminar' in talk and 'Online' in talk and '2027-05-04' in talk
        data = (output / 'data/fixture-dataset/index.html').read_text()
        assert 'fixture-vector.svg' in data and 'fixture-animation.gif' in data and 'cite.bib' in data
        listing = (output / 'news/index.html').read_text()
        assert listing.index('record-fixture-tie-a') < listing.index('record-fixture-tie-b')
        for lang in ('', 'zh/'):
            listing = (output / lang / 'publications/index.html').read_text()
            ids = re.findall(r'\bid=[\"\']?(paper-[A-Za-z0-9_-]+)', listing)
            selected = ['paper-fixture-' + ident for ident in
                        ('selected-a', 'section-only', 'selected-tie-a', 'selected-tie-b', 'selected-b', 'selected-auto', 'regular-priority')]
            assert [i for i in ids if i in selected] == selected
            assert listing.index('year-2028') < listing.index('year-2027') < listing.index('year-2026')
            assert 'paper-fixture-hidden-feature' not in listing
            assert all(ids.count(i) == 1 for i in selected)
            home = (output / lang / 'index.html').read_text()
            home_ids = re.findall(r'\bid=[\"\']?(home-fixture-[A-Za-z0-9_-]+)', home)
            assert home_ids == ['home-fixture-' + ident for ident in
                                ('formal-year', 'selected-accepted', 'selected-a', 'selected-tie-a', 'selected-tie-b', 'selected-b', 'selected-auto')]
            selected_ids = {i.removeprefix('home-') for i in home_ids}
            assert home_ids == ['home-' + i.removeprefix('paper-') for i in ids
                                if i.removeprefix('paper-') in selected_ids]
            assert 'home-fixture-section-only' not in home
            assert ('亮点' if lang else 'Highlights') in home
            assert 'home-fixture-hidden-feature' not in home
        if os.environ.get('TEST_SCENARIO_BROWSER') == '1':
            run(['node','scripts/test_browser.cjs'],repo,env | {'TEST_SCREENSHOTS':''})
    # Generator validation and its refusal to overwrite are part of the maintenance workflow.
    command=['python3','scripts/new_content.py','presentations','fixture-generated','--date','2027-01-01','--title-en','Generated oral','--title-zh','生成的口头报告','--event','Meeting']
    run(command,repo)
    assert subprocess.run(command,cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode != 0
    run(['python3','scripts/validate_content.py'],repo)
    # No selections is a valid editorial state in every section.
    for group in ('publications', 'resources', 'presentations', 'news'):
        for path in (repo / 'data' / group).glob('*.yaml'):
            data = yaml.safe_load(path.read_text())
            data.setdefault('display', {}).update(featured=False, home=False)
            path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
    env = os.environ | {'HUGO_BASEURL': 'https://example.org/'}
    run(['python3','scripts/validate_content.py'],repo,env)
    run(['npm','run','build'],repo,env)
    run(['python3','scripts/check_links.py','public'],repo,env)
    for lang in ('', 'zh/'):
        home = (repo / 'public' / lang / 'index.html').read_text()
        listing = (repo / 'public' / lang / 'publications/index.html').read_text()
        assert 'home-story' not in home and 'feature-label' not in home
        assert 'publication-featured' not in listing
print('Content scenarios OK: content types, statuses, assets, versions, generator, multiple featured papers, formal/fallback year priority, shared home/section sequence, partial selections, hidden/no selections and stable ties; root/project paths.')
