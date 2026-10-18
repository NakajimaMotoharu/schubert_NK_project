import re
import unittest
import pg5240_startup_view_selected as role


class PrimitiveViewScope(unittest.TestCase):
    def test_existing9_new8_inventory_and_fixed64_oracle_lengths(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        counts={}
        for name in role.VIEW:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),raw.count('@Test'))
            self.assertEqual(len(set(methods)),len(methods))
            counts[name.rpartition('.')[2]]=len(methods)
        self.assertEqual(counts,{'StartupAdmissionFileTest':9,'StartupAdmissionViewOwnerTest':8})
        self.assertEqual(len(role.extra_suites()),67)
        raw=(folder/'dev/codex/schubert/nk/batch/file/StartupAdmissionViewOwnerTest.java').read_text()
        for field in ('TYPE','SUPPRESSED','WINNER'):
            values=re.search(r'String\[\] '+field+r' = \{(.*?)\};',raw,re.S).group(1)
            rows=re.findall(r'"([A-Za-z0-9]+)"',values)
            self.assertEqual(len(rows),4)
            self.assertTrue(all(len(row)==16 for row in rows))

    def test_two_semantic_and_seven_bounded_nested_candidates(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),25)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),55)
        self.assertIn(role.PREFIX+'StartupAdmissionFile$ViewOwner.class',role.selected.EXTRA_CHANGED)


if __name__=='__main__':unittest.main()
