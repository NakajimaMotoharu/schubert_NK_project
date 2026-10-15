"""Literal parent identity/time fault matrix plus complete all-original observer namespace."""
import copy
import json
import unittest
from pyflakes.api import check
from pg3066_browser_resume_post import existing_parent_metadata, payload
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema


class Retained(unittest.TestCase):
    def test_explicit_original_parent_and_finite_clock_bounds(self):
        root, directory, target = '/run/systemd/system', '/run/systemd/system/x.d', '/run/systemd/system/x.d/z.conf'
        root_meta = [28, 4000, 0, 0, 0o40755, 3, 60, 10, 10]
        parent_meta = [28, 4564, 0, 0, 0o40755, 2, 40, 20, 20]
        initial = {root: {'metadata': root_meta, 'sha256': None}, directory: {'metadata': parent_meta, 'sha256': None}}
        prepared = copy.deepcopy(initial)
        prepared[directory]['metadata'] = [28, 4564, 0, 0, 0o40755, 2, 60, 100, 200]
        prepared[target] = {'metadata': [28, 6000, 0, 0, 0o100644, 1, 3, 100, 200], 'sha256': 'independent'}
        args = (root, directory, target, 100, 200, b'abc')
        self.assertIsNone(existing_parent_metadata(initial, prepared, *args))
        for name, index, value in [(root, 1, 4001), (directory, 0, 29), (directory, 1, 4565), (directory, 2, 1), (directory, 3, 1), (directory, 4, 0o40700), (directory, 5, 3), (directory, 6, 39), (directory, 7, 99), (directory, 8, 201), (target, 0, 29), (target, 1, 0), (target, 1, 4564), (target, 1, 4000), (target, 2, 1), (target, 3, 1), (target, 4, 0o100600), (target, 5, 2), (target, 6, 4), (target, 7, 99), (target, 8, 201)]:
            bad = copy.deepcopy(prepared)
            bad[name]['metadata'][index] = value
            with self.subTest(name=name, index=index, value=value), self.assertRaises(ValueError):
                existing_parent_metadata(initial, bad, *args)
        for bad in [{root: initial[root]}, {**initial, target: prepared[target]}]:
            with self.assertRaises(ValueError):
                existing_parent_metadata(bad, prepared, *args)

    def test_complete_post_scope_and_retirement_before_new_projection(self):
        old = json.loads((W / 'pg3040-current-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
        seals = {n: old['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
        raw = payload(seals)
        self.assertEqual(0, check('HASHES={}\nRECEIPT="sealed"\n' + raw, '<latest complete post>'))
        for literal in ['pg3064-browser-resume-preparation-v1', 'pg3060-browser-resume-tools-v1', 'zz-pg3060-once-resume.conf', 'len(rows) == 24', 'existing_parent_metadata', 'retainedOriginalParent']:
            self.assertIn(literal, raw)
        self.assertLess(raw.index("runtime_contract['same_except_runtime'](before,after,exec_record)"), raw.index('after,fresh_private,exec_record=independent_resume_delta(after)'))


if __name__ == '__main__':
    unittest.main()
