import re
import unittest
import pg5404_process_query_selected as entry

NAMES=('queryown001LiteralTwentyFourFailurePriorityRows',
    'queryown002FactoryAndNullBoundariesNeverReleaseUnownedResource',
    'queryown003SharedAndPreexistingExceptionsKeepIdentityWithoutSelfSuppression',
    'queryown004ParallelScopesRetainDistinctOwnersAndReverseNestedRelease',
    'queryown005SystemctlDefersNullButOwnsEveryPriorGetter',
    'queryown006InspectorRejectsEachMissingGetterBeforeNextInBothModes',
    'queryown007StreamingDeadlineAndDrainCancellationUseIndependentMonotonicVectors')


class QueryScope(unittest.TestCase):
    def test_original_query_suites_and_six_new_methods_are_exact(self):
        folder=entry.selected.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
        for name,count in [('SystemctlStateSourceTest',8),('InspectorUnitProbeTest',11),('ProcessResourceScopeTest',7)]:
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

    def test_query_ports_reject_common_io_normalization_or_legacy_use(self):
        from pg5406_process_query_bytecode import query_sites
        def method(kinds):
            return {'header':'fixture','ops':[(index,'invokedynamic',kind) for index,kind in enumerate(kinds)]+
                [(3,'invokestatic','ProcessResourceScope.acquire:')],'handlers':[]}
        ports=['ResourceScope$Acquire;','java/util/function/Consumer;','ProcessResourceScope$OwnedQuery;']
        self.assertEqual(len(query_sites([method(ports)])),1)
        for invalid in [ports[:2],['ResourceScope$Acquire;','ResourceScope$Release;','ResourceScope$OwnedAction;'],ports[::-1]]:
            with self.assertRaises(ValueError):query_sites([method(invalid)])
        with self.assertRaises(ValueError):
            query_sites([{'header':'old','ops':[(0,'invokestatic','ProcessResourceScope.use:')],'handlers':[]}])

    def test_success_path_never_executes_null_only_rejection(self):
        from pg5138_factory_bytecode import positive_path
        method={'header':'fixture','handlers':[], 'ops':[(0,'astore_1',''),(1,'aload_1',''),
            (2,'ifnull','5'),(3,'aload_1',''),(4,'goto','8'),(5,'aload_1',''),
            (6,'invokestatic','Objects.requireNonNull:'),(7,'checkcast','Process'),(8,'putfield','process'),(9,'return','')]}
        self.assertEqual(positive_path(method,0,None,'nonnull'),[0,1,2,3,4,8])
        bad={'header':'bad','handlers':[],'ops':[(0,'invokestatic','Objects.requireNonNull:'),(1,'return','')]}
        with self.assertRaises(ValueError):positive_path(bad,0,None,'nonnull')


if __name__=='__main__':unittest.main()
