"""Literal fixtures, no Production method or observed DB used as expected."""
import copy
import unittest
from pg639_resume_oracle import validate


def fixture():
    steps = ('BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION',
             'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN',
             'CLEAN_TRANSFER', 'CLEAN_EXPIRY')
    rows = []
    for i in range(494):
        rows.append({'id': i + 1, 'run_id': 'historical', 'business_date': '2026-10-08',
                     'step': 'historical', 'attempt': 1, 'status': 'SUCCESS'})
    added = []
    for i, step in enumerate(steps):
        rows[i] = dict(rows[i], step=step, business_date='2026-10-09',
                       run_id=('e49243d5-de84-4714-8612-6912ddc17e9e' if i < 2
                               else '3a53b979-fa01-47dd-92a6-7b26affcfb5c'))
        added.append({'id': 495 + i, 'run_id': 'e49243d5-de84-4714-8612-6912ddc17e9e',
                      'business_date': '2026-10-09', 'step': step, 'attempt': 2,
                      'started_at': '2026-10-08T20:15:00+00:00', 'ended_at': '2026-10-08T20:15:00+00:00',
                      'status': 'SKIPPED', 'target_count': 0, 'success_count': 0,
                      'failure_count': 0, 'byte_count': 0, 'error_code': 'ALREADY_SUCCESSFUL',
                      'error_summary': 'step already successful for business date',
                      'expiry_cutoff_at': '2026-10-01T18:32:42.140966+00:00' if i == 9 else None,
                      'expiry_before_count': 0 if i == 9 else None, 'expiry_after_count': 0 if i == 9 else None})
    old = {'schubert.batch_runs': rows, **{'table' + str(i): [{'id': i, 'value': None}] for i in range(23)}}
    new = copy.deepcopy(old); new['schubert.batch_runs'].extend(added)
    backup = {'fixed/file': {'metadata': [0, 1], 'sha256': 'literal'}}
    return old, new, backup, copy.deepcopy(backup)


class Oracle(unittest.TestCase):
    def test_normal_reordered_all_rows(self):
        values = fixture(); values[1]['schubert.batch_runs'].reverse()
        self.assertEqual(validate(*values)['newSameRunSkippedAttempts'], 10)

    def test_each_new_column_corruption(self):
        for key in fixture()[1]['schubert.batch_runs'][-1]:
            with self.subTest(key=key):
                values = fixture(); values[1]['schubert.batch_runs'][-1][key] = None
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    validate(*values)

    def test_old_rows_backup_or_tables_changed(self):
        for mutation in ('old', 'backup', 'other', 'extra', 'missing', 'duplicate'):
            with self.subTest(mutation=mutation):
                a, b, c, d = fixture()
                if mutation == 'old': b['schubert.batch_runs'][0]['attempt'] = 99
                if mutation == 'backup': d['fixed/file']['sha256'] = 'changed'
                if mutation == 'other': b['table0'][0]['value'] = 'changed'
                if mutation == 'extra': b['table0'].append({'id': 42})
                if mutation == 'missing': b['schubert.batch_runs'].pop()
                if mutation == 'duplicate': b['schubert.batch_runs'][-1] = b['schubert.batch_runs'][-2]
                with self.assertRaises(ValueError): validate(a, b, c, d)


if __name__ == '__main__': unittest.main()
