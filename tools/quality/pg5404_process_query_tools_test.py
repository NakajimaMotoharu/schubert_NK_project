import re
import unittest
import pg5404_process_query_selected as entry

NAMES=('queryown001LiteralTwentyFourFailurePriorityRows',
    'queryown002FactoryAndNullBoundariesNeverReleaseUnownedResource',
    'queryown003SharedAndPreexistingExceptionsKeepIdentityWithoutSelfSuppression',
    'queryown004ParallelScopesRetainDistinctOwnersAndReverseNestedRelease',
    'queryown005SystemctlDefersNullButOwnsEveryPriorGetter',
    'queryown006InspectorRejectsEachMissingGetterBeforeNextInBothModes')


class QueryScope(unittest.TestCase):
    def test_original_query_suites_and_six_new_methods_are_exact(self):
        folder=entry.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
        for name,count in [('SystemctlStateSourceTest',8),('InspectorUnitProbeTest',11),('ProcessResourceScopeTest',6)]:
            raw=(folder/(name+'.java')).read_text()
            methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),count);self.assertEqual(raw.count('@Test'),count)
            if name=='ProcessResourceScopeTest':self.assertEqual(tuple(methods),NAMES)

    def test_literal_priority_table_is_independent_and_full(self):
        raw=(entry.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeTest.java').read_text()
        table=re.findall(r'"([Nbcre]+)"',re.search(r'String\[\] winner\s*=\s*(.*?);',raw,re.S).group(1))
        self.assertEqual(len(table),6)
        for row in range(6):
            self.assertEqual(len(table[row]),4)
            for col in range(4):
                expected='N' if row==col==0 else 'b' if row>0 and (col<2 or row>=4) else 'cleanup'
                observed=table[row][col]
                self.assertEqual(observed if observed in 'Nb' else 'cleanup',expected)

    def test_explicit_growth_preserves_all_prior_additions_and_removal(self):
        entry.configure()
        self.assertEqual(entry.selected.EXTRA_ADDED,entry.previous.ADDED|entry.ADDED)
        self.assertEqual(entry.selected.EXTRA_REMOVED,entry.previous.REMOVED)
        self.assertEqual(764+len(entry.selected.EXTRA_ADDED)-len(entry.selected.EXTRA_REMOVED),767)
        self.assertEqual(len(entry.extra_suites()),106)
        self.assertTrue(entry.REQUIRED<=entry.selected.EXTRA_CHANGED)
        self.assertEqual(entry.repetitions(),entry.previous.repetitions())


if __name__=='__main__':unittest.main()
