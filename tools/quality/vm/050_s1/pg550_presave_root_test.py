"""Independent fixed identity and new-only replay prevention; management only."""
import ast
import copy
from pathlib import Path
import unittest

RAW=Path(__file__).with_name('pg550_presave_root_handoff_v1.py').read_text()
NODE=next(n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name=='identity')
ENV={};exec(compile(ast.Module(body=[NODE],type_ignores=[]),'<fixed root identity test>','exec'),ENV)


class Test(unittest.TestCase):
    def test_identity(self):
        valid={'pid':575778,'ticks':4093969,'argv':'4dfeee7365ffb8538dc3b9896ffb8ce7b9a1fd918a2083991d0038337b11a994','uid':['0']*4,'parent':575776,'children':set()}
        args=(575778,4093969,valid['argv'],575776)
        self.assertTrue(ENV['identity'](valid,*args))
        self.assertFalse(ENV['identity'](None,*args))
        for key,value in [('pid',True),('ticks',4093970),('parent',1),('argv','0'*64),('uid',['0','1','0','0']),('children',[1])]:
            bad=copy.deepcopy(valid);bad[key]=value
            self.assertFalse(ENV['identity'](bad,*args))

    def test_fixed_reservation_action_and_names(self):
        self.assertIn("phase='ROOT_ONLY'",RAW);self.assertIn('PID=575778',RAW)
        self.assertNotIn('childfd=',RAW)
        self.assertEqual(RAW.count('signal.pidfd_send_signal(parentfd,signal.SIGTERM)'),1)
        self.assertLess(RAW.index("save('term-reserved.private.json'"),RAW.index('signal.pidfd_send_signal(parentfd,signal.SIGTERM)'))
        wrapper=Path(__file__).with_name('pg550_presave_root_native_v1.py').read_text()
        self.assertIn("RUN='PG550-presave-root-'",wrapper)
        self.assertIn("assert prior['toolHashes']==hashes",wrapper)
        self.assertNotIn('PG545-runtime',wrapper)


if __name__=='__main__':unittest.main()
