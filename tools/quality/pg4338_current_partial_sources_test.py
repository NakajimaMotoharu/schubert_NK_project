"""Independent literal current epoch/owner and rejected-pair evidence contract."""
import ast
import copy
import json
import unittest
from pyflakes.api import check
import pg4338_current_partial_sources as subject
from pg4164_retained_pair_profile_test import PairProfileTest


class CurrentPartial(unittest.TestCase):
    def test_full_closure_static_and_compilation(self):
        for name, raw in subject.files().items():
            with self.subTest(name=name):
                compile(raw, '<' + name + '>', 'exec')
                self.assertEqual(0, check(raw, '<' + name + '>'))

    def test_current_pair_bindings_not_prior_pair(self):
        raw = subject.profile_source()
        env = {}
        exec(raw, env)
        self.assertEqual((815726, 815643), (env['JAVA'], env['PYTHON']))
        for old in ['790010', '789928', '14181503', 'session-921', 'pg4146-', 'pg4112-']:
            self.assertNotIn(old, raw)
        self.assertIn('session-970.scope', raw)
        self.assertEqual(98, len(env['JVM_FDS']))
        self.assertEqual({'0', '1', '2', '3', '4', '6', '7'}, env['PY_FDS'])

    def test_independent_current_pair_positive_and_every_fd_authority_negative(self):
        # Reuse the earlier independent fixed fixture, NOT production profile output.
        profile = {}
        exec(subject.profile_source(), profile)
        for oldpid in [790010, 789928]:
            raw = json.dumps(PairProfileTest().actor(oldpid))
            for old, new in [('790010', '815726'), ('789928', '815643'), ('789926', '815641'),
                             ('14181503', '15409721'), ('14180650', '15408795'),
                             ('session-921', 'session-970'), ('pg4146-complete-signed-owned-recovery-v1', 'pg4316-current-failed-dispatch-v1'),
                             ('pg4112-canonical-epoch-owned-tools-v1', 'pg4312-current-failed-owned-tools-v1'),
                             ('ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2', '5312514ace02eda3eb8f4f4941095f5e334dc00859d52aa2a5a811a626c7b698')]:
                raw = raw.replace(old, new)
            fixed = json.loads(raw)
            self.assertTrue(profile['stable'](fixed, copy.deepcopy(fixed), 100))
            for fd in fixed['fds']:
                for field, value in [('target', '/foreign'), ('fdinfo', 'flags:\t01\n'), ('metadata', None)]:
                    after = copy.deepcopy(fixed)
                    after['fds'][fd][field] = value
                    with self.subTest(pid=fixed['pid'], fd=fd, field=field), self.assertRaises(ValueError):
                        profile['stable'](fixed, after, 100)
            for field in fixed['authority']:
                after = copy.deepcopy(fixed)
                after['authority'][field] = 'foreign'
                with self.subTest(authority=field), self.assertRaises(ValueError):
                    profile['stable'](fixed, after, 100)

    def test_rejected_pair_is_saved_before_failure_without_retry(self):
        records = []
        env = {'save_private': lambda name, value: records.append((name, value))}
        exec(subject.mismatch_source(), env)
        before = {key: {} for key in ['units', 'actors', 'detailedActors', 'durable', 'native', 'startup', 'runtime']}
        before['database'] = {'rows': {}}
        env['same_values'](before, copy.deepcopy(before))
        self.assertEqual([], records)
        for key in ['units', 'actors', 'detailedActors', 'durable', 'native', 'startup', 'runtime', 'databaseRows']:
            after = copy.deepcopy(before)
            if key == 'databaseRows':
                after['database']['rows']['changed'] = [1]
            else:
                after[key]['changed'] = 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                env['same_values'](before, after)
            self.assertEqual(('rejected-pair.private.json', {'before': before, 'after': after, 'changedKeys': [key]}), records[-1])

    def test_caddy_is_observe_only_and_other_five_have_one_action(self):
        raw = subject.partial()
        tree = ast.parse(raw)
        stop = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'stop')
        self.assertIsInstance(stop.body[0], ast.If)
        self.assertEqual("unit == 'caddy.service'", ast.unparse(stop.body[0].test))
        self.assertIsInstance(stop.body[0].body[-1], ast.Return)
        self.assertNotIn('systemctl', ast.get_source_segment(raw, stop.body[0]))
        self.assertEqual(1, ast.get_source_segment(raw, stop).count("'stop'"))
        self.assertIn('newStopCount', raw)
        self.assertIn('all37StartupEntriesPreserved', raw)
        self.assertIn('original58917Normal', raw)

    def test_independent_post_uses_partial_but_retains_full_original_reference(self):
        raw = subject.post()
        self.assertIn("RECOVERY='/var/lib/pgpt-s1-preservation/pg4340-current-partial-v1-recover'", raw)
        self.assertIn("before['actors']=={u:a for u,a in reference['actors'].items()if u!='caddy.service'}", raw)
        self.assertIn('pg4306-current-failed-authority-read-v1', raw)


if __name__ == '__main__':
    unittest.main()
