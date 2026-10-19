import copy
import json
import unittest
from pyflakes.api import checkPath
import pg5582_confined_map_context as entry


class ConfinementContexts(unittest.TestCase):
    def test_all21_individual_source_and_actual_physical_contexts(self):
        prior=json.loads((entry.BASE/'PG5560-snapshot-static-findings-v1/manifest.json').read_bytes())
        old=json.loads((entry.BASE/'PG5550-current3900-cases/qualification.json').read_bytes())['allPhysicalMainSha256']
        selected=json.loads((entry.ROOT.parent/'pgpt-runs/PG379/pg5566-private-monitor-green-v2/manifest.safe.json').read_bytes())['physicalMain']['sha256']
        rows,witnesses=entry.context_rows(prior,selected,old)
        self.assertEqual(len(rows),21);self.assertEqual(sum(r['kind']=='LOCAL_SCRATCH'for r in rows),19)
        self.assertEqual(len(witnesses),12)
        bad=copy.deepcopy(prior)
        next(r for r in bad['findings']if r['rule']=='UseConcurrentHashMap')['sourceSha256']='0'*64
        with self.assertRaises(ValueError):entry.context_rows(bad,selected,old)
        wrong=dict(selected);wrong['api:dev/codex/schubert/nk/api/security/AuthContextCodec.class']='0'*64
        with self.assertRaises(ValueError):entry.context_rows(prior,wrong,old)

    def test_unknown_row_does_not_get_rule_wide_waiver(self):
        prior=json.loads((entry.BASE/'PG5560-snapshot-static-findings-v1/manifest.json').read_bytes());prior['findings']=[r for r in prior['findings']if r['rule']=='UseConcurrentHashMap'][:-1]
        old=json.loads((entry.BASE/'PG5550-current3900-cases/qualification.json').read_bytes())['allPhysicalMainSha256']
        with self.assertRaises(ValueError):entry.context_rows(prior,old,old)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
