"""SSC232 exact Java only ownership counterexamples; no actual operations."""
import ast
import copy
import unittest
from pg663_handoff import PRELUDE,payload


class Test(unittest.TestCase):
    def test_fixed_owner(self):
        env={};node=next(n for n in ast.parse(PRELUDE).body if isinstance(n,ast.FunctionDef)and n.name=='process_identity')
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<owner>','exec'),env)
        v={'pid':2141065,'ticks':11112630,'parent':2141063,'argv':'4406b878234be0e15d15334e7238c029f27ebd0e8a85a63624546608d67c6367','uid':['0']*4,'exe':'/opt/jdk-25.0.4/bin/java','children':set()}
        self.assertTrue(env['process_identity'](v))
        for k,bad in({'pid':2141063,'ticks':11112629,'parent':0,'argv':'old','uid':['999']*4,'exe':'/bin/java','children':{1}}).items():
            x=copy.deepcopy(v);x[k]=bad;self.assertFalse(env['process_identity'](x),k)
        for k in v:
            x=copy.deepcopy(v);del x[k];self.assertFalse(env['process_identity'](x))
        self.assertFalse(env['process_identity'](None))

    def test_single_reserved_pidfd_no_business_actions(self):
        raw=payload();ast.parse(raw)
        self.assertEqual(raw.count('signal.pidfd_send_signal(fd,signal.SIGTERM)'),1)
        self.assertLess(raw.index("persist('term-reservation.private.json'"),raw.index('signal.pidfd_send_signal'))
        for value in('owned(True)','owned(False)','allPeerAdvisoryFlock0','before==capture()and before==capture()',"'oldCloseUNKNOWN':True",'8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8'):
            self.assertIn(value,raw)
        for value in('SIGKILL','systemctl\',\'start','daemon-reload','delete from','update schubert','reset-failed'):
            self.assertNotIn(value,raw)


if __name__=='__main__':unittest.main()
