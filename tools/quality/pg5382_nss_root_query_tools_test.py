import re
import unittest
import pg5380_nss_root_query_selected as entry
import pg5384_nss_root_query_public as public


class NssRootInventory(unittest.TestCase):
    def test_new_four_and_original_ten_eighteen_have_one_to_one_ids(self):
        original={'FixedServiceIdentityTest':10,'RootStartupContextTest':18}
        for cls,(_,names) in public.CASES.items():
            module='bootstrap' if '.bootstrap.' in cls else 'batch'
            path=entry.selected.ROOT/('src/schubert-nk-'+module+'/src/test/java/'+cls.replace('.','/')+'.java')
            raw=path.read_text();methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),original[cls.rpartition('.')[2]]+2)
            self.assertEqual(len(methods),raw.count('@Test'))
            self.assertEqual(tuple(n for n in methods if n.startswith(('nssown','rootqueryown'))),names)

    def test_bounded_cross_module_delta_and_credit_never_double_counts_old_related(self):
        entry.configure()
        self.assertEqual((len(entry.selected.EXTRA_CHANGED),len(entry.selected.EXTRA_DEBUG),len(entry.extra_suites())),(61,185,102))
        self.assertEqual({k.split(':',1)[0] for k in entry.REQUIRED},{'bootstrap','batch'})
        ids=public.revalidated_case_ids(owner_new=True)
        self.assertEqual(sum(v['newInThisChange'] for v in ids.values()),4)
        self.assertEqual(sum(v['newInThisChange'] for v in public.revalidated_case_ids().values()),0)
        self.assertEqual(len({v['testId'] for v in ids.values()}),len(ids))


if __name__=='__main__':unittest.main()
