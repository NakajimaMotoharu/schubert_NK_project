import ast
import copy
import hashlib
import json
from types import SimpleNamespace
import unittest
from pyflakes.api import check
import pg4360_pool_bound_partial_sources as subject
import pg4338_current_partial_sources as prior


class BoundSources(unittest.TestCase):
    def test_whole_closure_static_and_protected_inputs_unchanged(self):
        for name, raw in subject.files().items():
            with self.subTest(name=name):
                compile(raw, name, 'exec')
                self.assertEqual(0, check(raw, '<' + name + '>'))
        def literals(raw):
            names = {'JAVA_B64', 'ANNOTATION_B64', 'PARENT_SOURCE', 'PROTOCOL_SOURCE', 'NATIVE_SOURCE', 'SIGNED_SOURCE'}
            return {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(raw).body
                    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names}
        self.assertEqual(literals(prior.partial()), literals(subject.partial()))

    def test_boundary_full_two_reads_and_every_changed_key_saved_then_rejected(self):
        keys = ['units', 'actors', 'detailedActors', 'durable', 'native', 'startup', 'runtime', 'ordinaryDatabaseFds']
        fixed = {key: {} for key in keys}; fixed['database'] = {'rows': {}}
        for key in keys + ['databaseRows']:
            after = copy.deepcopy(fixed)
            if key == 'databaseRows': after['database']['rows']['changed'] = 1
            else: after[key]['changed'] = 1
            samples = iter([fixed, after]); records = []
            env = {'capture_snapshot': lambda: next(samples), 'save_pair': lambda name, data: records.append((name, data))}
            exec(subject.BOUNDARY, env)
            with self.subTest(key=key), self.assertRaises(ValueError): env['snapshot']()
            self.assertEqual('rejected-boundary-pair', records[0][0])
            self.assertEqual({'before': fixed, 'after': after, 'changed': [key]}, records[0][1])
            with self.assertRaises(StopIteration): next(samples)
        samples = iter([fixed, copy.deepcopy(fixed)])
        env = {'capture_snapshot': lambda: next(samples), 'save_pair': lambda *_: self.fail('no rejected pair')}
        exec(subject.BOUNDARY, env); self.assertEqual(fixed, env['snapshot']())

    def test_failed_evidence_save_never_becomes_success(self):
        fixed = {key: {} for key in ['units', 'actors', 'detailedActors', 'durable', 'native', 'startup', 'runtime', 'ordinaryDatabaseFds']}
        fixed['database'] = {'rows': {}}; after = copy.deepcopy(fixed); after['detailedActors']['foreign'] = 1
        samples = iter([fixed, after])
        def failed_save(*_): raise OSError('independent failure fixture')
        env = {'capture_snapshot': lambda: next(samples), 'save_pair': failed_save}
        exec(subject.BOUNDARY, env)
        with self.assertRaises(OSError): env['snapshot']()

    def test_old_socket_not_certified_and_current_reference_is_explicit(self):
        raw = subject.keeper()
        self.assertIn('Old fd93 TCP ownership remains unclassified', raw)
        self.assertIn('pg4356-current-pool-witness-v1/observed.private.json', raw)
        self.assertIn("save_pair('rejected-reference-pair'", raw)
        self.assertIn("fd_contract['same_details']", raw)
        self.assertIn("reference['ordinaryDatabaseFds']", raw)

    def test_split_full_images_preserve_per_file_limit_and_second_failure(self):
        parts = {'before': {'full': 'x' * 4000}, 'after': {'full': 'y' * 4000}}
        self.assertGreater(len(json.dumps(parts).encode()), 5000)
        written = {}
        def writer(name, value):
            encoded = json.dumps(value, sort_keys=True).encode()
            self.assertLessEqual(len(encoded), 5000)
            written[name] = encoded
            return hashlib.sha256(encoded).hexdigest()
        def require(value):
            if value is not True: raise ValueError('fixture rejected')
        env = {'private_record': writer, 'require': require}
        exec(subject.SAVING, env); env['save_pair']('rejected-test', parts)
        index = json.loads(written['rejected-test.index.private.json'])
        self.assertTrue(index['complete'])
        for name, digest in index['partSha256'].items(): self.assertEqual(digest, hashlib.sha256(written[name]).hexdigest())
        written.clear()
        def fail_second(name, value):
            if '.after.' in name: raise OSError('independent second file failure')
            return writer(name, value)
        env['private_record'] = fail_second
        with self.assertRaises(OSError): env['save_pair']('rejected-test', parts)
        self.assertEqual(['rejected-test.before.private.json'], list(written))

    def test_second_bind_failure_preserves_captured_parts_before_propagation(self):
        records = []; samples = {'database': {'peers': []}}
        source = "ROLES={}\ncalls=0\ndef bind(*args):\n global calls\n calls+=1\n if calls==2:raise ValueError('independent second bind failure')\n return {}\n"
        class EmptyTcp:
            def __init__(self, *_): pass
            def read_text(self): return 'header\n'
        env = {'FD_SOURCE': source, 'snapshot': lambda: copy.deepcopy(samples), 'Path': EmptyTcp,
               'pwd': SimpleNamespace(getpwnam=lambda _: SimpleNamespace(pw_uid=108, pw_gid=112)),
               'tcp_pair': None, 'endpoint': None, 'save_pair': lambda name, data: records.append((name, data))}
        exec(subject.CAPTURE, env)
        env['capture_snapshot']()
        with self.assertRaises(ValueError): env['capture_snapshot']()
        self.assertEqual('rejected-bind', records[0][0])
        self.assertEqual({'snapshot': samples, 'tcp': [], 'servers': {}}, records[0][1])

    def test_partial_compares_full_server_witness_and_uses_split_pair(self):
        raw = subject.partial()
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'same_values')
        text = ast.get_source_segment(raw, node)
        self.assertIn("'ordinaryDatabaseFds'", text)
        self.assertIn("save_pair('rejected-pair'", text)


if __name__ == '__main__':
    unittest.main()
