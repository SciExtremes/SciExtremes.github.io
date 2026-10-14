"""Exercise supported content scenarios and actionable failures in isolated temporary records."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import yaml
from content_model import validate_records, read_yaml, normalize


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, group, record):
        path = self.root / 'data' / group / (record['id'] + '.yaml')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False))
        return path

    def check(self):
        return validate_records(self.root)

    def test_online_invited_oral_without_location_or_material(self):
        self.write('presentations', dict(id='talk', date='2027-01-01', event='Seminar', kind='oral', event_type='seminar', role='invited', participation='online'))
        records, errors = self.check()
        self.assertEqual(errors, [])
        self.assertEqual(records['presentations']['talk']['links'], [])
        self.assertEqual(records['presentations']['talk']['location'], '')

    def test_seminar_and_sparse_display_defaults(self):
        self.write('presentations', dict(id='talk', date='2027-01-01', event='Seminar', kind='seminar', display={'visible': False}))
        records, errors = self.check()
        self.assertEqual(errors, [])
        self.assertFalse(records['presentations']['talk']['display']['visible'])
        self.assertFalse(records['presentations']['talk']['display']['featured'])

    def test_all_publication_types_and_conditional_fields(self):
        variants = [('article', 'journal'), ('conference', 'booktitle'), ('chapter', 'booktitle'), ('report', 'institution'), ('preprint', 'repository')]
        for kind, venue in variants:
            self.write('publications', dict(id=kind, date='2027-01-01', type=kind, title='Title & methods', authors=['E. Researcher'], year=2027, **{venue: 'Venue'}))
        records, errors = self.check()
        self.assertEqual(errors, [])
        self.assertEqual(records['publications']['preprint']['status'], 'preprint')
        self.assertTrue(all(not r['doi'] for r in records['publications'].values()))

    def test_accepted_without_doi_venue_or_formal_year(self):
        self.write('publications', dict(id='accepted', date='2027-01-01', title='Accepted study', authors=['Example Researcher'], status='accepted', author_roles={'corresponding': ['Example Researcher']}))
        self.assertEqual(self.check()[1], [])

    def test_year_precision_and_date_range(self):
        self.write('news', dict(id='year', date='2027-01-01', date_precision='year'))
        self.write('presentations', dict(id='range', date='2027-05-02', end_date='2027-05-04', event='Meeting', kind='oral'))
        self.assertEqual(self.check()[1], [])

    def test_multiresource_named_links_and_structured_citation(self):
        for ident in ('data1', 'data2'):
            self.write('resources', dict(id=ident, date='2027-01-01', name=ident, resource_type='dataset', version='2.0', links=[{'label': 'accessData', 'url': 'https://example.org/' + ident, 'name': {'en': 'Historical', 'zh': '历史'}}], citation={'title': 'Dataset', 'authors': ['E. Researcher'], 'year': 2027}))
        self.assertEqual(self.check()[1], [])

    def test_other_requires_bilingual_description(self):
        self.write('presentations', dict(id='other', date='2027-01-01', event='Event', kind='other'))
        self.assertIn('kind_label', '\n'.join(self.check()[1]))

    def test_unknown_fields_types_and_missing_required_are_specific(self):
        self.write('news', dict(id='broken', date='not-a-date', date_precison='year', links={}))
        errors = '\n'.join(self.check()[1])
        for text in ('date_precison', 'date must be date', 'links must be list'):
            self.assertIn(text, errors)

    def test_casefold_collision_and_duplicate_yaml(self):
        self.write('news', dict(id='Entry', date='2027-01-01'))
        self.write('news', dict(id='entry', date='2027-01-01'))
        self.assertIn('collision', '\n'.join(self.check()[1]))
        path = self.root / 'duplicate.yaml'
        path.write_text('kind: oral\nkind: poster\n')
        with self.assertRaises(yaml.YAMLError):
            read_yaml(path)

    def test_bad_associations_and_author_roles_do_not_crash(self):
        self.write('publications', dict(id='paper', date='2027-01-01', title='Title', authors=['Author'], status='accepted', author_roles={'corresponding': ['Other']}, related_version_ids=['paper']))
        errors = '\n'.join(self.check()[1])
        self.assertIn('exact authors', errors)

    def test_invalid_display_and_article_number_conflict(self):
        self.write('publications', dict(id='paper', date='2027-01-01', title='Title', authors=['Author'], status='accepted', pages='1-3', article_number='e001', display={'visible': 'yes'}))
        errors = '\n'.join(self.check()[1])
        self.assertIn('display.visible', errors)
        self.assertIn('pages or article_number', errors)

    def test_normalization_does_not_mutate_shared_defaults(self):
        first = normalize('news', {'display': {'visible': False}})
        first['links'].append({'label': 'PDF', 'url': '/example'})
        second = normalize('news', {})
        self.assertEqual(second['links'], [])
        self.assertTrue(second['display']['visible'])
        self.assertEqual(second['display']['order'], 0)

    def test_multiple_publication_features_and_home_highlights(self):
        for ident in ('a', 'b', 'c'):
            self.write('publications', dict(id=ident, date='2027-01-01', title='Example paper',
                       authors=['Example Researcher'], status='accepted',
                       display={'featured': True, 'home': ident != 'c', 'order': 10}))
        self.assertEqual(self.check()[1], [])

    def test_home_requires_featured_even_when_hidden(self):
        for ident, visible in (('visible', True), ('hidden', False)):
            self.write('news', dict(id=ident, date='2027-01-01',
                       display={'visible': visible, 'home': True, 'featured': False}))
        records, errors = self.check()
        for ident in ('visible', 'hidden'):
            self.assertTrue(any(f'{ident}.yaml' in e and 'requires display.featured: true' in e for e in errors))
            self.assertFalse(records['news'][ident]['display']['featured'])

    def test_home_does_not_imply_featured_through_a_default(self):
        self.write('news', dict(id='story', date='2027-01-01', display={'home': True}))
        self.assertIn('requires display.featured: true', '\n'.join(self.check()[1]))

    def test_order_requires_nonnegative_integer(self):
        for value in (-1, True, '10', 1.5):
            with self.subTest(value=value):
                self.write('news', dict(id='story', date='2027-01-01', display={'order': value}))
                self.assertIn('display.order must be a nonnegative integer', '\n'.join(self.check()[1]))
        self.write('news', dict(id='story', date='2027-01-01', display={'order': 0}))
        self.assertEqual(self.check()[1], [])

    def test_nonpublication_feature_limit_counts_visible_records_only(self):
        for ident, visible in (('shown', True), ('hidden-a', False), ('hidden-b', False)):
            self.write('news', dict(id=ident, date='2027-01-01',
                       display={'visible': visible, 'featured': True, 'home': True}))
        self.assertEqual(self.check()[1], [])
        self.write('news', dict(id='second', date='2027-01-01', display={'featured': True}))
        self.assertIn('at most one visible featured record', '\n'.join(self.check()[1]))


if __name__ == '__main__':
    unittest.main()
