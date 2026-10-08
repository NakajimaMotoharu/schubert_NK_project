"""Literal independent fixture adapted from SS341, no Production expected generation."""
import copy
import json
import unittest
from pg563_batch_backup_oracle_test import Test as PriorVectors
from pg582_backup_oracle import validate


class Test(unittest.TestCase):
    def setUp(self):
        prior = PriorVectors()
        prior.setUp()
        self.files = prior.files
        self.rows = prior.new['schubert.batch_runs'][:2]
        self.manifest = prior.m
        self.manifest['runId'] = 'b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'
        self.manifest['cutoff'] = '2026-10-08T07:36:21.802335Z'
        self.manifest['startedAt'] = '2026-10-08T07:36:23.000000Z'
        self.manifest['contentFinishedAt'] = '2026-10-08T07:36:24.000000Z'
        for row, field in zip(self.rows, ('databaseStep', 'configurationStep')):
            row.update(run_id=self.manifest['runId'], started_at='2026-10-08T07:36:22.000000Z', ended_at='2026-10-08T07:36:25.000000Z')
            self.manifest[field]['startedAt'] = row['started_at']

    def raw(self, manifest=None):
        return (json.dumps(self.manifest if manifest is None else manifest, separators=(',', ':')) + '\n').encode()

    def test_success_and_row_negatives(self):
        self.assertEqual(0, validate([], self.rows, self.raw(), self.files)['allOldBatchRowsProtected'])
        for field, value in [('id', True), ('attempt', 2), ('run_id', 'foreign'), ('byte_count', 0),
                             ('failure_count', 1), ('status', 'SKIPPED'), ('error_code', 'x'), ('expiry_before_count', 0)]:
            rows = copy.deepcopy(self.rows)
            rows[0][field] = value
            with self.assertRaises(ValueError):
                validate([], rows, self.raw(), self.files)

    def test_manifest_bytes_null_foreign_and_duplicate(self):
        for field, value in [('runId', 'foreign'), ('cutoff', None), ('startedAt', '2026-10-08T07:36:20.000000Z')]:
            m = copy.deepcopy(self.manifest)
            m[field] = value
            with self.assertRaises(ValueError):
                validate([], self.rows, self.raw(m), self.files)
        for raw in (None, self.raw() + b' ', self.raw().replace(b'"format":', b'"format":"duplicate","format":')):
            with self.assertRaises(ValueError):
                validate([], self.rows, raw, self.files)
        for name in self.files:
            files = dict(self.files)
            files[name] += b'x'
            with self.assertRaises(ValueError):
                validate([], self.rows, self.raw(), files)


if __name__ == '__main__':
    unittest.main()
