import subprocess
import unittest
import pg6796_web_early_cleanup_proof as p
import pg6798_web_correlation_selected as selected


class EarlyCleanupSourceTest(unittest.TestCase):
    def test_required_early_declaration_and_all_previous_state_regions(self):
        before=subprocess.check_output(['git','show',p.old.OLD+':'+p.old.MAIN],cwd=p.ROOT,text=True)
        after=(p.ROOT/p.old.MAIN).read_text()
        self.assertTrue(p.expand_early(before,after)['emptyPreparedBeforeBind'])
        late=after.replace('    var closing = Optional.<IOException>empty();\n','',1).replace(
          '} catch (RuntimeException | Error failure) {','} catch (RuntimeException | Error failure) {\n      var closing = Optional.<IOException>empty();',1)
        with self.assertRaises(ValueError):p.expand_early(before,late)
        with self.assertRaises(ValueError):p.expand_early(before,after.replace('if (started) serverStopped = true;','serverStopped = true;',1))

    def test_measured_four_owners_are_not_the_physical_changed_owner_guard(self):
        f=selected.qualification_definition()
        self.assertEqual(4,len(f.__globals__['MEASURED_TARGETS']))
        self.assertIn(1669,f.__code__.co_consts)
        self.assertNotIn(1667,f.__code__.co_consts)


if __name__=='__main__':unittest.main()
