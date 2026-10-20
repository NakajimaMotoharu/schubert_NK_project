import copy
import json
import unittest
from pg6092_current3985_static_join import BASE, W, ROOT, reviewed_result, ordered_pairs, bind_one, validate_rationales


class CurrentDispositionDefinitionTest(unittest.TestCase):
    def test_invalid_or_missing_qualification_never_becomes_current_pass(self):
        with self.assertRaises(ValueError):
            reviewed_result('not-a-hash', 'not-a-hash')

    def test_original431_text_restoration_and_strict623_only_without_whole_claim(self):
        old = json.loads((BASE/'PG6068-current-static3979-v1/findings.json').read_bytes())
        restorations = json.loads((BASE/'PG6100-rationale-lineage-v1/restorations.json').read_bytes())
        by_id = {r['findingId']: r for r in restorations}
        restored = copy.deepcopy(old)
        for r in restored:
            if r['findingId'] in by_id:
                r['reason'] = r['priorReason'] = by_id[r['findingId']]['reason']
        validate_rationales(restored)
        before = json.loads((BASE/'PG6060-current3979-cases/qualification.json').read_bytes())['allPhysicalMainSha256']
        current = json.loads((W/'pg6082-web-factory-qualification-v1/manifest.safe.json').read_bytes())['allPhysicalMainSha256']
        raw = json.loads((W/'pg6082-web-factory-qualification-v1/findings.safe.json').read_bytes())
        pairs = ordered_pairs(restored, raw); eligible = {r['findingId']: r for r in restored if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
        count = 0
        for row in raw:
            pair = pairs.get(row['findingId']); prior = eligible.get(pair[0]['findingId']) if pair else None
            new, kind = bind_one(row, [prior] if prior else [], (ROOT/row['sourcePath']).read_bytes(), before, current)
            if kind == 'REBOUND':
                self.assertTrue(new['reason'].strip())
                self.assertTrue(new['currentWholeJoinPending'])
                self.assertEqual([], new['currentWholeCaseRefs'])
                count += 1
        self.assertEqual(623, count)
        self.assertEqual(431, len(by_id))


if __name__ == '__main__':
    unittest.main()
