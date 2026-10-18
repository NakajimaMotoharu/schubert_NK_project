"""Independent sealed/enriched distinction and complete new-only witness entry."""
import copy
import hashlib
import json
import inspect
import unittest
from pyflakes.api import check, checkPath
import pg5092_retained_pair_full_proof as proof
import pg5098_failed_phase_full_proof as entry
import pg5094_failed_phase_full_proof_test as previous


class Schema(unittest.TestCase):
    def fixture(self):
        return {'source': 'literal-source', 'manifestSha256': 'literal-bom',
                'rows': {'table' + str(n): [] for n in range(24)},
                'native': {'/run/schubert-nk/pt-coverage': {},
                           **{'/run/schubert-nk/pt-coverage/test/' + str(n) + '.exec': {} for n in range(86)}}}

    def qualify(self, value):
        raw = json.dumps(value, sort_keys=True).encode()
        return proof.native_reference(raw, hashlib.sha256(raw).hexdigest(), 'literal-source', 'literal-bom')

    def test_independent_enriched_contract_and_missing_sealed_key_refuses(self):
        value = self.fixture()
        self.assertEqual(value['native'], self.qualify(value))
        for key, invalid in [('source', 'foreign'), ('manifestSha256', 'foreign'), ('rows', {}), ('native', None)]:
            wrong = {**value, key: invalid}
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.qualify(wrong)
        sealed = copy.deepcopy(value)
        del sealed['native']
        with self.assertRaises(ValueError):
            self.qualify(sealed)
        for bad in (None, b'{}'):
            with self.assertRaises(ValueError):
                proof.native_reference(bad, '0' * 64, 'literal-source', 'literal-bom')
        wrong = copy.deepcopy(value)
        wrong['native'].pop(next(iter(wrong['native'])))
        with self.assertRaises(ValueError):
            self.qualify(wrong)

    def test_actual_factory_uses_hashqualified_enriched_not_sealed_native(self):
        raw = entry.payload()
        self.assertEqual(0, check(raw, '<schema-complete current witness>'))
        for literal in ('pg5080-current-bootstrap-before-v1/after.private.json', proof.role.BASELINE,
                        'native_reference(reference_raw, ENRICHED_SHA, SOURCE, BOM)'):
            self.assertTrue(literal in raw, literal)
        self.assertTrue("native == after['native']" not in raw)
        for path in (proof.__file__, entry.__file__, __file__):
            self.assertEqual(0, checkPath(path))


raw = inspect.getsource(previous.FailedPhaseEntry)
ns = {**vars(previous), '__file__': __file__, 'entry': entry.previous}
# Same real-entry test code, using the new-only namespace and final payload.
ns['entry'] = __import__('types').SimpleNamespace(**{**vars(entry.previous), 'SLOT': entry.SLOT, 'payload': entry.payload})
ns['entry'].main = __import__('types').FunctionType(entry.previous.main.__code__, vars(ns['entry']))
exec(compile(raw, '<new schema entry independent tests>', 'exec'), ns)
FailedPhaseEntry = ns['FailedPhaseEntry']


if __name__ == '__main__':
    unittest.main()
