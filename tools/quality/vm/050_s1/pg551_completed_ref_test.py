"""Fixed pair identity/source reservation, independent literals; management PT0."""
import ast
import copy
from pathlib import Path
import unittest

RAW=Path(__file__).with_name('pg551_completed_ref_handoff_v1.py').read_text()
NODE=next(n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name=='identity')
ENV={};exec(compile(ast.Module(body=[NODE],type_ignores=[]),'<fixed pair identity>','exec'),ENV)


class Test(unittest.TestCase):
    def test_fixed_root_ref_identity(self):
        for pid,ticks,parent,sha,children in [(576780,4161990,576778,'3be3de301dcbd99e087eae25622d42718f1d167ae96db6cbb353c592342aedcc',{576809}),(576809,4162106,576780,'48093440b74bdf9b4ed0808a61d6526904a468331bb422b5e2844aa79d660e73',set())]:
            value={'pid':pid,'ticks':ticks,'parent':parent,'argv':sha,'uid':['0']*4,'children':children}
            self.assertTrue(ENV['identity'](value,pid,ticks,sha,parent))
            for key,invalid in [('pid',True),('ticks',ticks+1),('argv','0'*64),('uid',['0','1','0','0']),('parent',1),('children',[])]:
                bad=copy.deepcopy(value);bad[key]=invalid
                self.assertFalse(ENV['identity'](bad,pid,ticks,sha,parent))
            self.assertFalse(ENV['identity'](None,pid,ticks,sha,parent))

    def test_child_then_root_only_and_reservation(self):
        self.assertLess(RAW.index("save('term-reserved.private.json'"),RAW.index('signal.pidfd_send_signal(childfd'))
        self.assertLess(RAW.index('signal.pidfd_send_signal(childfd'),RAW.index('signal.pidfd_send_signal(parentfd'))
        self.assertEqual(RAW.count('signal.pidfd_send_signal'),2)
        self.assertIn("phase='NONE'",RAW)
        wrapper=Path(__file__).with_name('pg551_completed_ref_native_v1.py').read_text()
        self.assertIn("assert prior['toolHashes']==hashes",wrapper)
        self.assertIn("RUN='PG551-completed-ref-'",wrapper)


if __name__=='__main__':unittest.main()
