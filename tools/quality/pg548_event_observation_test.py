"""487 append-only correction semantics, shared group windows; Production PT0."""
import json
from pathlib import Path
import unittest

P=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')


class Test(unittest.TestCase):
    def test_nonoverlapping_correction(self):
        values=[json.loads(line)for line in P.read_text().splitlines()]
        self.assertEqual(len(values),len({v['eventId']for v in values}))
        names=['PGPT-20261008-'+n for n in('0053','0054','0055','0056')]
        rows={v['eventId']:v for v in values if v['eventId']in names}
        correction={v['targetEventId']:v for v in rows[names[-1]]['observationCorrections']}
        self.assertEqual(set(correction),set(names[1:3]))
        total=0
        for name in names:
            row=rows[name];before=row['quotaBefore'];after=row['quotaAfter'];expected=row['observedSharedPp']
            if name in correction:before=correction[name]['correctedQuotaBefore'];expected=correction[name]['correctedObservedSharedPp']
            self.assertEqual(before['resetsAt'],after['resetsAt'])
            self.assertLessEqual(before['fetchedAtJST'],after['fetchedAtJST'])
            delta=after['usedPercent']-before['usedPercent'];self.assertGreaterEqual(delta,0);self.assertEqual(delta,expected);total+=delta
            self.assertIsNone(row['actualAllocatedPp']);self.assertIsNone(row['tokenTotals'])
        self.assertEqual(total,2)
        self.assertEqual(rows[names[0]]['quotaBefore']['usedPercent'],19)
        self.assertEqual(rows[names[-1]]['quotaAfter']['usedPercent'],21)


if __name__=='__main__':unittest.main()
