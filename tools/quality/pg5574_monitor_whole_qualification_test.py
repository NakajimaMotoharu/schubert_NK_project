import unittest
from pyflakes.api import check,checkPath
import pg5574_monitor_whole_qualification as entry


class WholeMonitorQualification(unittest.TestCase):
    def test_all_original3900_and_exact_five_independent_methods(self):
        self.assertEqual(set(entry.added_cases()),entry.ADDED)
        raw='PHYSICAL_KINDS='+repr(entry.PHYSICAL_KINDS)+'\n'+__import__('inspect').getsource(entry.physical_difference)+'\n'+entry.qualifier_source()
        self.assertEqual(check(raw,'<all3904 independent standalone>'),0)
        self.assertIn('source-full-PG5588',raw);self.assertIn('runs/PG5550-six-v1',raw)
        self.assertNotIn('runs/PG5414-six-v1',raw);self.assertIn('len(oldcases) == 3900',raw);self.assertIn('len(cases) == 3905',raw);self.assertIn('len(additions) == 5',raw)

    def test_every_raw_debug_difference_is_required_not_dropped(self):
        before={**{k:'a'*64 for k in entry.PHYSICAL_KINDS},**{f'api:Control{i}.class':'a'*64 for i in range(1653)}}
        candidate={k:('b'*64 if k in entry.PHYSICAL_KINDS else v)for k,v in before.items()}
        changes,same=entry.physical_difference(before,candidate,candidate)
        self.assertEqual(same,1653);self.assertEqual(len(changes),11)
        self.assertEqual(sum(c['physicalKind']=='DEBUG_ONLY'for c in changes),5)
        bad=dict(candidate);bad['api:Control0.class']='c'*64
        for current in({},bad,before):
            with self.assertRaises(ValueError):entry.physical_difference(before,current,current)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
