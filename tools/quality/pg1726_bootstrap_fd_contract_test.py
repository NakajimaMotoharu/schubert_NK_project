"""Independent current31/90 oracle; no guest, process or signal operations."""
import ast
import copy
import unittest
from pg1726_bootstrap_current_fd_handoff import payload
from pg1724_retained_handoff_test import ContractTest

class CurrentFdTest(ContractTest):
    def test_current_bootstrap_layout(self):
        raw=payload();node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='fresh_sole_parent')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual current pure guard>','exec'),ns);guard=ns['fresh_sole_parent']
        a={'pid':383695,'ticks':7281859,'argvSha256':'b'*64,'authority':{'Uid':'0'},'cgroup':'fixed','fds':{str(i):{'metadata':[28,i,0,0,16832,1,64,100,100],'target':'fixed'}for i in range(99)}}
        for n in ('31','90'):a['fds'][n]={'metadata':[28,1,0,0,16877,1,64,100,100],'target':'/run'}
        self.assertTrue(guard(a,copy.deepcopy(a),101))
        b=copy.deepcopy(a)
        for n in ('31','90'):b['fds'][n]['metadata'][7:]=[101,101]
        self.assertTrue(guard(a,b,101))
        for kind in ('oldLayout','oneOnly','target','otherTime','extra','missing','backward','future','bool','inode'):
            b=copy.deepcopy(a)
            if kind=='oldLayout':
                for n in ('29','32'):b['fds'][n]['target']='/run'
                b['fds']['31']['target']='fixed'
            elif kind=='oneOnly':b['fds']['31']['metadata'][7]=101
            elif kind=='target':b['fds']['31']['target']='/other'
            elif kind=='otherTime':b['fds']['29']['metadata'][7]=101
            elif kind=='extra':b['fds']['100']=b['fds']['10']
            elif kind=='missing':del b['fds']['10']
            elif kind=='backward':b['fds']['31']['metadata'][7]=99
            elif kind=='future':b['fds']['31']['metadata'][7]=102
            elif kind=='bool':b['fds']['31']['metadata'][0]=True
            else:b['fds']['31']['metadata'][1]=999
            with self.subTest(kind=kind),self.assertRaises(ValueError):guard(a,b,101)
        self.assertIn("fresh['fds']['31']['metadata']==fresh['fds']['90']['metadata']",raw)
        self.assertEqual(raw.count('terminate(383695,7281859,before,reserve,os.pidfd_open,send,wait,os.close)'),1)

if __name__=='__main__':unittest.main()
