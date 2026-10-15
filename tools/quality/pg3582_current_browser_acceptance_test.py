"""Final current readers and isolated mutation-free old/foreign authority negatives."""
import ast
import unittest
from pyflakes.api import check
import pg3582_current_browser_acceptance as root
import pg3580_current_browser_actual as browser
import pg3574_current_browser_resume_once as once


class CurrentAcceptance(unittest.TestCase):
    def test_final_terminal_rows_and_seal(self):
        value=root.live();binding={**value['binding'],'rootPid':value['rootPid']}
        for raw in [root.terminal_payload(binding),root.rows_payload(),root.seal_payload(binding)]:
            self.assertEqual(0,check(raw,'<whole new current reader>'))
            self.assertNotIn('PG2802',raw)
        seal=root.seal_payload(binding)
        self.assertIn(root.BEFORE,seal)
        self.assertIn('pg3574-current-browser-resume-once-v1/before.private.json',seal)
        oracle=next(ast.literal_eval(n.value)for n in ast.parse(seal).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE'for t in n.targets))
        self.assertIn("progress[0]['protected_count']==10",oracle)
        self.assertIn("row['attempt']==max(historical)+1",oracle)
        self.assertIn("row['status']=='SKIPPED'",oracle)
        self.assertIn('e1ee096d-370b-4ab9-915a-7c124207e854',oracle)

    def test_once_literal_and_cardinality_negative_predicates(self):
        raw=once.payload({'pg3572_watch_parent.py':'a'*64})
        tree=ast.parse(raw)
        nodes=[n.args[0]for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require']
        count=next(n for n in nodes if ast.unparse(n)=='len(records) == 28')
        for size,expected in [(10,False),(27,False),(28,True),(29,False)]:
            self.assertEqual(expected,eval(compile(ast.Expression(count),'<exact cardinality>','eval'),{'records':dict.fromkeys(range(size))}))
        condition=next(n for n in nodes if ast.unparse(n).startswith('declaration is not None and'))
        main='java dev.codex.schubert.nk.batch.file.MorningProcessMain'
        for argv,expected in [(None,False),(main,False),(main+' --resume foreign',False),(main+' --resume '+root.RUN,True),(main+' --resume '+root.RUN+' extra',False)]:
            declaration=None if argv is None else ('path',argv,False)
            self.assertEqual(expected,eval(compile(ast.Expression(condition),'<independent completed resume literal>','eval'),{'declaration':declaration}))

    def test_browser_current_owner_and_fresh_activation_guard(self):
        live=root.live();binding=live['binding']
        seal={'actualExit':0,'productionSource':root.SOURCE,'observedOwned':{}}
        terminal={'actualExit':0,'productionSource':root.SOURCE,'genuineParentDone':True,'proofHashes':{'done.private':'a'*64}}
        raw=browser.guard(seal,terminal,binding)
        self.assertIn(binding['activation']+'.done',raw)
        self.assertIn(root.SOURCE,raw)
        self.assertIn(root.BOM,raw)
        self.assertIn("'caddy.service','artemis.service']",raw)
        self.assertIn('context.verify_mode==ssl.CERT_REQUIRED',raw)
        self.assertNotIn('PG2802',raw)
        with self.assertRaises(ValueError):browser.guard({**seal,'productionSource':'foreign'},terminal,binding)


if __name__=='__main__':unittest.main()
