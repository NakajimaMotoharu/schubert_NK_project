import subprocess
import unittest
import pg6822_api_stop_result_equivalence as p
import pg6824_api_management_result_selected as selected


class ApiStopResultSourceTest(unittest.TestCase):
    def test_all_prior_tokens_and_exception_regions_match(self):
        before=subprocess.check_output(['git','show',p.OLD+':'+p.MAIN],cwd=p.ROOT,text=True);after=(p.ROOT/p.MAIN).read_text()
        self.assertEqual(5,p.expand_to_original(before,after)['fixedUnknownOutcomes'])
        late=after.replace('    var closing = Optional.<IllegalStateException>empty();\n','',1).replace(
          '} catch (RuntimeException | Error failure) {','} catch (RuntimeException | Error failure) {\n      var closing = Optional.<IllegalStateException>empty();',1)
        for bad in (late,after.replace('if (started.get()) serverStopped = true;','serverStopped = true;',1),
          after.replace('if (interrupted) Thread.currentThread().interrupt();','',1),
          after.replace('closing.ifPresent(ignored -> failure.addSuppressed(cleanupDiagnostic));','closing.ifPresent(failure::addSuppressed);',1)):
            with self.assertRaises(ValueError):p.expand_to_original(before,bad)

    def test_exact_selected_inventory_and_original_physical1669(self):
        _,counts=selected.inventory();self.assertEqual((30,11),(sum(counts.values()),len(counts)))
        self.assertIn('len(physical)==1669',selected.prior.runner(*selected.EXPECTED,{'api':['api/bootstrap/ApiManagementServer']}))
        self.assertIn(1669,selected.prior.qualification_definition().__code__.co_consts)


if __name__=='__main__':unittest.main()
