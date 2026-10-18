import hashlib
import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5416_ownership_whole_qualification as entry


class WholeQualification(unittest.TestCase):
    def test_all_original_cases_and_exact_eighty_two_source_additions(self):
        additions=entry.added_cases()
        self.assertEqual(len(additions),82);self.assertEqual(len(set(additions)),82)
        self.assertEqual(sum(name.startswith('queryown') for _,name in additions),7)
        raw=entry.qualifier_source()
        self.assertIn('len(oldcases) == 3814',raw);self.assertIn('len(additions) == 82',raw)
        self.assertIn('len(cases) == 3896',raw);self.assertIn("'suites': 562",raw)
        self.assertIn("'mainClasses': 1664",raw)
        self.assertIn("old = base / 'runs/PG5128-six-v1'",raw)
        self.assertIn('allSixFormatBeforeAnyPt',raw)

    def test_actual_named_added_removed_modified_are_exact(self):
        old={f'batch:C{i}.class':hashlib.sha256(str(i).encode()).hexdigest() for i in range(1654)}
        new=dict(old);del new['batch:C0.class'];new['batch:C1.class']='a'*64
        added={f'batch:New{i}.class' for i in range(11)}
        new.update({key:'b'*64 for key in added})
        with patch.multiple(entry,MODIFIED={'batch:C1.class'},ADDED=added,REMOVED={'batch:C0.class'}):
            rows,unchanged=entry.physical_difference(old,new,new)
            self.assertEqual(len(rows),13);self.assertEqual(unchanged,1652)
            for variant in ({},dict(new,foreign='c'*64),dict(new,**{'batch:C2.class':'d'*64})):
                with self.assertRaises(ValueError):entry.physical_difference(old,variant,new)
            corrupt=dict(new);corrupt['batch:C2.class']='not a digest'
            with self.assertRaises(ValueError):entry.physical_difference(old,corrupt,corrupt)

    def test_current_selected_expected_bytes_are_not_unbuilt_success(self):
        prior,candidate,difference=entry.candidate_main()
        self.assertEqual(prior['productionSource'],entry.entry.previous.SOURCE)
        self.assertEqual(len(candidate),1664)
        self.assertEqual(len(difference['added']),11);self.assertEqual(len(difference['removed']),1)
        self.assertEqual(difference['removed'],{'batch:dev/codex/schubert/nk/batch/platform/BackupArchiveProcess$StdinOwner.class'})
        declarations='\n'.join(name+'=set()' for name in ('MODIFIED','ADDED','REMOVED'))
        raw='import json\n'+declarations+'\n'+inspect.getsource(entry.physical_difference)+'\n'+entry.qualifier_source()+'\nprint(json.dumps({}))\n'
        self.assertEqual(check(raw,'<standalone independent all1664>'),0)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
