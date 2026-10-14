#!/usr/bin/env python3
"""Verify reuse with a different profile, subject, IDs and navigation in an isolated copy."""
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import yaml
from content_model import ROOT


def read(path):
    return yaml.safe_load(path.read_text())


def write(path, value):
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False))


def run(args, cwd, env):
    subprocess.run(args, cwd=cwd, env=env, check=True)


with TemporaryDirectory(prefix='academic-template-test-') as temp:
    repo = Path(temp) / 'site'
    def ignored(directory, names):
        exclusions = {'__pycache__', '.git', '.hugo_build.lock'}
        if Path(directory) == ROOT:
            exclusions |= {'public', 'resources', 'node_modules'}
        return set(names) & exclusions
    shutil.copytree(ROOT, repo, ignore=ignored)
    (repo / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
    profile = read(repo / 'data/profile.yaml')
    profile['en']['name'], profile['zh']['name'] = 'Example Researcher', '示例研究者'
    profile['en']['role'], profile['zh']['role'] = 'Research Fellow', '研究员'
    profile['affiliation'] = {'name': {'en':'Example University', 'zh':'示例大学'}, 'url':'https://example.edu/'}
    profile['author_names'] = ['Example Researcher', 'E. Researcher']
    profile['links'] = [{'label':'Email', 'url':'mailto:researcher@example.edu', 'languages':['en','zh']}]
    profile['education'], profile['experience'] = [], []
    write(repo / 'data/profile.yaml', profile)
    for group in ('publications','resources','presentations','news'):
        for path in (repo / 'data' / group).glob('*.yaml'):
            record = read(path)
            if group == 'publications':
                record['title'] = 'Example academic study ' + record['id']
                record['authors'] = ['Example Researcher']
            elif group == 'resources':
                record['name'] = 'Example resource ' + record['id']
            write(path, record)
    for path in (repo / 'content').rglob('index.md'):
        front = path.read_text().split('---',2)[1]
        meta = yaml.safe_load(front)
        if 'record_id' not in meta:
            continue
        meta.pop('translated_title',None)
        meta['summary'] = 'Example academic content.'
        if path.parts[-3] != 'publications':
            meta['title'] = 'Example item ' + meta['record_id']
        path.write_text('---\n' + yaml.safe_dump(meta,allow_unicode=True,sort_keys=False) + '---\n\nExample description.\n')
    focus = {'en':{'words':['Methods','Evidence','Models'],'introduction':'An example research programme.'},'zh':{'words':['方法','证据','模型'],'introduction':'一个示例研究方向。'}}
    write(repo / 'data/focus.yaml',focus)
    questions = read(repo / 'data/questions.yaml')
    id_map = {}
    for index, question in enumerate(questions,1):
        ident = f'topic-{index}'
        id_map[question['id']] = ident
        question.update(id=ident,label=f'RQ{index}',title={'en':f'Example topic {index}','zh':f'示例问题{index}'},paragraphs={'en':['Purpose.','Approach.','Next steps.'],'zh':['研究目标。','研究方法。','下一步工作。']},paper_ids=[],data_ids=[])
    write(repo / 'data/questions.yaml',questions)
    framework = read(repo / 'data/framework.yaml')
    for key in ('title','description','context','caption'):
        framework[key] = {'en':'Example framework text','zh':'示例框架文字'}
    for index, stage in enumerate(framework['stages'],1):
        stage['id'] = f'phase-{index}'
        stage['title'] = {'en':f'Phase {index}','zh':f'阶段{index}'}
        stage['sq_ids'] = [id_map[q] for q in stage['sq_ids']]
        for term in stage['terms']:
            term.update(label={'en':'Example concept','zh':'示例概念'},detail={'en':'Concept description','zh':'概念说明'},paper_id='')
    for index, modifier in enumerate(framework['modifiers'],1):
        modifier['id'] = f'factor-{index}'
        for key in ('title','detail','target'):
            modifier[key] = {'en':'Example modifier','zh':'示例因素'}
    write(repo / 'data/framework.yaml',framework)
    menu = read(repo / 'config/_default/menus.yaml')
    for index, entry in enumerate(reversed(menu['main']),1):
        entry['weight'] = index*10
    write(repo / 'config/_default/menus.yaml', menu)
    for lang in ('en','zh'):
        strings = read(repo / f'i18n/{lang}.yaml')
        strings['researchQuestionsIntro']['other'] = 'Example research questions.' if lang=='en' else '示例研究问题。'
        strings['research']['other'] = 'Topics' if lang=='en' else '课题'
        write(repo / f'i18n/{lang}.yaml',strings)
    env = os.environ | {'HUGO_BASEURL':'https://example.org/academic-site/'}
    for enabled in (True,False):
        if not enabled:
            (repo / 'data/framework.yaml').unlink()
        layout = read(repo / 'data/research_layout.yaml')
        layout['framework_enabled'] = enabled
        write(repo / 'data/research_layout.yaml',layout)
        run(['python3','scripts/validate_content.py'],repo,env)
        run(['npm','run','build'],repo,env)
        run(['python3','scripts/check_links.py','public'],repo,env)
        output = (repo / 'public/research/index.html').read_text()
        assert ('framework-title' in output) == enabled
        assert 'RQ1' in output and 'topic-1' in output
        if os.environ.get('TEST_TEMPLATE_BROWSER') == '1':
            run(['node','scripts/test_browser.cjs'],repo,env | {'TEST_SCREENSHOTS':''})
print('Template OK: alternate identity/content, configured navigation, arbitrary Research IDs and optional framework.')
