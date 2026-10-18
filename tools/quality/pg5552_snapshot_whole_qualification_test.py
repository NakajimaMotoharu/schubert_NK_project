import copy
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5552_snapshot_whole_qualification as entry


class Qualification(unittest.TestCase):
    def test_exactly_one_actual_change_and_all1664_current_bytes(self):
        key='api:dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'
        old={**{f'batch:Fixture{i}.class':'a'*64 for i in range(1663)},key:'b'*64};new={**old,key:'c'*64}
        changes,unchanged=entry.physical_difference(old,new,copy.deepcopy(new));self.assertEqual(len(changes),1);self.assertEqual(unchanged,1663)
        for bad in({**new,'extra':'d'*64},{**new,key:None},{**new,'batch:Fixture0.class':'f'*64},old):
            with self.assertRaises(ValueError):entry.physical_difference(old,bad,new)

    def test_real_four_added_source_cases_and_every_old_identity_preserved(self):
        rows=entry.added_cases();self.assertEqual(len(rows),4)
        prior,candidate=entry.candidate_main();self.assertEqual(len(candidate),1664);self.assertEqual(prior['tests'],3896)
        raw=inspect.getsource(entry.physical_difference)+'\n'+entry.qualifier_source();self.assertEqual(check(raw,'<independent complete3900>'),0)
        self.assertIn('len(oldcases) == 3896',raw);self.assertIn('len(cases) == 3900',raw);self.assertIn('len(additions) == 4',raw)
        for path in('runs/PG5550-six-v1','source-full-PG5550','runs/PG5414-six-v1','transfer/PG5550-source.tar'):
            self.assertIn(path,raw)
        for marker in('allSixFormatBeforeAnyPt','flakyFailure','xmlHashes','allPhysicalMainSha256',"'formalAccepted': False"):
            self.assertIn(marker,raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
