import ast
import copy
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
            env = {'capture_snapshot': lambda: next(samples), 'private_record': lambda name, data: records.append((name, data))}
            exec(subject.BOUNDARY, env)
            with self.subTest(key=key), self.assertRaises(ValueError): env['snapshot']()
            self.assertEqual('rejected-boundary-pair.private.json', records[0][0])
            self.assertEqual({'before': fixed, 'after': after, 'changedKeys': [key]}, records[0][1])
            with self.assertRaises(StopIteration): next(samples)
        samples = iter([fixed, copy.deepcopy(fixed)])
        env = {'capture_snapshot': lambda: next(samples), 'private_record': lambda *_: self.fail('no rejected pair')}
        exec(subject.BOUNDARY, env); self.assertEqual(fixed, env['snapshot']())

    def test_failed_evidence_save_never_becomes_success(self):
        fixed = {key: {} for key in ['units', 'actors', 'detailedActors', 'durable', 'native', 'startup', 'runtime', 'ordinaryDatabaseFds']}
        fixed['database'] = {'rows': {}}; after = copy.deepcopy(fixed); after['detailedActors']['foreign'] = 1
        samples = iter([fixed, after])
        def failed_save(*_): raise OSError('independent failure fixture')
        env = {'capture_snapshot': lambda: next(samples), 'private_record': failed_save}
        exec(subject.BOUNDARY, env)
        with self.assertRaises(OSError): env['snapshot']()

    def test_old_socket_not_certified_and_current_reference_is_explicit(self):
        raw = subject.keeper()
        self.assertIn('Old fd93 TCP ownership remains unclassified', raw)
        self.assertIn('pg4356-current-pool-witness-v1/observed.private.json', raw)
        self.assertIn('rejected-reference-pair.private.json', raw)
        self.assertIn("fd_contract['same_details']", raw)
        self.assertIn("reference['ordinaryDatabaseFds']", raw)


if __name__ == '__main__':
    unittest.main()
