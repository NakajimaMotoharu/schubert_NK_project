import copy
import unittest
from pg4102_failed_done_recovery_protocol import ORDER, Recovery, preserved_tree


class RecoveryProtocolTest(unittest.TestCase):
    def callbacks(self, failure=None):
        calls = []
        reservations = set()
        def call(name, unit):
            calls.append((name, unit))
            if failure == len(calls): raise OSError('independent boundary failure')
            if name == 'reserve':
                if unit in reservations: raise FileExistsError('durable once')
                reservations.add(unit)
            return True
        subject = Recovery(*(lambda unit, name=name: call(name, unit)
                             for name in ['verify', 'reserve', 'stop', 'terminal', 'record']))
        return subject, calls, reservations

    def test_exact_six_order_and_external_proof_each_boundary(self):
        subject, calls, reservations = self.callbacks()
        for unit in ORDER: subject.one(unit)
        subject.complete()
        self.assertEqual(list(ORDER), [u for n, u in calls if n == 'stop'])
        for i, unit in enumerate(ORDER):
            self.assertEqual([(n, unit) for n in ['verify','reserve','verify','stop','terminal','verify','record']], calls[i*7:(i+1)*7])
        self.assertEqual(set(ORDER), reservations)

    def test_every_failure_prefix_prevents_retry_revoke_or_next_unit(self):
        for failure in range(1, 43):
            with self.subTest(failure=failure):
                subject, calls, _ = self.callbacks(failure)
                with self.assertRaises(OSError):
                    for unit in ORDER: subject.one(unit)
                stopped = [u for n, u in calls if n == 'stop']
                self.assertEqual(len(stopped), len(set(stopped)))
                index = min((failure-1)//7, 5)
                with self.assertRaises(ValueError): subject.one(ORDER[index])
                with self.assertRaises(ValueError): subject.complete()
                with self.assertRaises(ValueError): subject.plan.revoke()

    def test_wrong_unit_and_missing_or_false_terminal(self):
        for unit in [None, '', ORDER[1], 'schubert-nk-backup.service']:
            subject, calls, _ = self.callbacks()
            with self.assertRaises(ValueError): subject.one(unit)
            self.assertEqual([], calls)
        for result in [None, False, 1, 'true']:
            subject, calls, _ = self.callbacks()
            subject.terminal = lambda unused: result
            with self.assertRaises(ValueError): subject.one(ORDER[0])
            self.assertFalse(any(n == 'record' for n, u in calls))

    def test_finite_namespace_metadata_and_whole_preservation(self):
        before = {'/fixed': {'metadata': [1,2,0,0,33152,1,8,10,11], 'sha256': 'f'*64},
                  '/epoch': {'metadata': [1,3,0,0,33152,1,8,10,11], 'sha256': 'a'*64},
                  '/dir': {'metadata': [1,4,0,0,16832,2,4096,10,11], 'sha256': None}}
        after = copy.deepcopy(before)
        after['/epoch']['metadata'][1] = 5
        after['/epoch']['sha256'] = 'b'*64
        after['/dir']['metadata'][7:] = [20,21]
        self.assertTrue(preserved_tree(before, after, ('/epoch',), ('/dir',)))
        for key in [0,2,3,4,5]:
            bad = copy.deepcopy(after); bad['/epoch']['metadata'][key] += 1
            with self.assertRaises(ValueError): preserved_tree(before, bad, ('/epoch',), ('/dir',))
        for kind in ['extra', 'missing', 'fixed', 'directoryInode', 'null']:
            bad = copy.deepcopy(after)
            if kind == 'extra': bad['/foreign'] = before['/fixed']
            elif kind == 'missing': del bad['/fixed']
            elif kind == 'fixed': bad['/fixed']['sha256'] = '0'*64
            elif kind == 'directoryInode': bad['/dir']['metadata'][1] += 1
            else: bad['/epoch']['metadata'] = None
            with self.assertRaises(ValueError): preserved_tree(before, bad, ('/epoch',), ('/dir',))


if __name__ == '__main__': unittest.main()
