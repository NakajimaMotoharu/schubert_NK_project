import ast
import unittest
from pg1306_ordinary_publication_sources import sources


class ActualOrdinaryPublicationNamespaceTest(unittest.TestCase):
    def test_complete_actual_namespace_keeps_done_and_no_cold_or_refreeze(self):
        files=sources();java=files['Pg1306OrdinaryPublication.java'];refs=files['pg1306_native_refs.py']
        for n,s in files.items():
            if n.endswith('.py'):ast.parse(s)
        self.assertIn('State.ISSUED',java)
        self.assertIn('transitionOriginal(epoch,done)',java)
        self.assertIn('invalidExpected',java)
        self.assertNotIn('freezeCandidate()',java)
        self.assertNotIn('def place_candidate',refs)
        self.assertIn("same_value(first,json.loads(baseline))",refs)
        self.assertIn("exchange_io.move_old_link(directory,save_fd",refs)
        self.assertIn('for path,fd in new_fds.items()',refs)
        self.assertIn("phase_observe('link-staged')",refs)
        self.assertIn("phase_observe('exchanged')",refs)
        helper=ast.parse(files['pg1306_native_owned_stop.py']);env={}
        nodes=[n for n in helper.body if isinstance(n,ast.FunctionDef)and n.name in {'require','placement_family','placement_action'}]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual complete publication boundary>','exec'),env)
        self.assertTrue(env['placement_family']([b'/opt/jdk-25.0.4/bin/java',b'-cp',b'fixed',b'Pg1306OrdinaryPublication',b'activate',b'']))
        for action,state in [('before','before'),('epoch','before'),('approval','epoch'),('exchange','approval'),('terminal','old-linked-private'),('release','old-linked-private')]:self.assertTrue(env['placement_action'](action,state))
        for action,state in [('epoch','epoch'),('approval','before'),('exchange','before'),('place','before'),('release','epoch'),(None,'before'),('before',None)]:
            with self.assertRaises(ValueError):env['placement_action'](action,state)


if __name__=='__main__':unittest.main()
