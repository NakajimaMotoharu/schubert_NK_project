import subprocess
import unittest
import pg6780_web_management_result_selected as p
import pg6781_web_stop_result_equivalence as proof


class WebStopResultDefinitionTest(unittest.TestCase):
    def test_exact_unchanged_independent_inventory_and1669(self):
        cases,counts=p.inventory();self.assertEqual((28,10),(sum(counts.values()),len(counts)))
        raw=p.runner(*p.EXPECTED,{'web':['web/bootstrap/WebManagementServer']})
        self.assertIn('len(physical)==1669',raw);self.assertNotIn('len(physical)==1667',raw)
        self.assertEqual(1669,p.qualification_definition().__code__.co_consts[p.qualification_definition().__code__.co_consts.index(1669)])

    def test_source_preserves_state_and_all_exception_regions(self):
        before=subprocess.check_output(['git','show',p.OLD+':'+p.MAIN],cwd=p.ROOT,text=True)
        after=(p.ROOT/p.MAIN).read_text()
        self.assertTrue(proof.expand_to_original(before,after)['exceptionRegionUnchanged'])
        for mutation in (after.replace('closing = result.stopFailure(java.time.Duration.ofSeconds(30));',
            'result.stopFailure(java.time.Duration.ofSeconds(30)).ifPresent(failure::addSuppressed);',1),
          after.replace('if (started) serverStopped = true;','serverStopped = true;',1),
          after.replace('Thread.currentThread().interrupt();','Thread.interrupted();',1),
          after.replace('if (!started) return Optional.of(new IOException(STOP_UNCONFIRMED));','',1)):
            with self.assertRaises(ValueError):proof.expand_to_original(before,mutation)


if __name__=='__main__':unittest.main()
