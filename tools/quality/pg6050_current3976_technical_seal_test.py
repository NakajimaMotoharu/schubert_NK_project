import copy
import json
import unittest
import pg6050_current3976_technical_seal as t


class TechnicalSealCannotUpgradeAnotherSourceTest(unittest.TestCase):
    def test_real_immutable_proofs_and_independent_negative_mutations(self):
        q, s, d = [json.loads((t.BASE/t.REFS[k][0]).read_bytes()) for k in ('whole', 'static', 'review')]
        p = json.loads((t.W/'pg6044-remaining33-static-v2/manifest.safe.json').read_bytes())
        t.validate(q, s, d, p)
        for field, bad in [('productionSource', 'other-source'), ('tests', 3975), ('FESFlakyNotRun', 1)]:
            with self.assertRaises(ValueError):
                t.validate(dict(q) | {field: bad}, s, d, p)
        changed = copy.deepcopy(p); changed['auxClassHashes'][next(iter(changed['auxClassHashes']))] = '0'*64
        with self.assertRaises(ValueError):
            t.validate(q, s, d, changed)


if __name__ == '__main__':
    unittest.main()
