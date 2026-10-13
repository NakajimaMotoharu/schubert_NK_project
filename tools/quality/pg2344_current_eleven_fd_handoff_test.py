import ast
import unittest
from copy import deepcopy
from pg2344_current_eleven_fd_handoff import payload,fresh_child


class ChildFresh(unittest.TestCase):
    def test_only_shared_run_chrono_and_all_other_fields_exact(self):
        fd={'metadata':[28,1,0,0,16877,2,40,100,100],'target':'/run'}
        old={'pid':101050,'ticks':1808864,'argvSha256':'fixed','authority':{},'cgroup':'fixed','busNames':['fixed'],'fds':{str(i):deepcopy(fd)for i in range(11)}}
        now=deepcopy(old);now['fds']['5']['metadata'][7:]=[110,111]
        parent={'fds':{'31':deepcopy(now['fds']['5']),'90':deepcopy(now['fds']['5'])}}
        self.assertTrue(fresh_child(old,now,parent,120))
        for name in now['fds']:
            for field in range(9):
                if name=='5'and field in [7,8]:continue
                changed=deepcopy(now);changed['fds'][name]['metadata'][field]+=1
                with self.assertRaises(ValueError):fresh_child(old,changed,parent,120)
        for key in ['pid','ticks','argvSha256','authority','cgroup','busNames']:
            changed=deepcopy(now);changed[key]=None
            with self.assertRaises(ValueError):fresh_child(old,changed,parent,120)
        for value in [99,121]:
            changed=deepcopy(now);changed['fds']['5']['metadata'][7]=value
            with self.assertRaises(ValueError):fresh_child(old,changed,parent,120)
        raw=payload()
        self.assertTrue('terminate(101050,1808864'in raw)
        self.assertTrue('terminate(101019,1808679'in raw)
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(ast.parse(raw))))


if __name__=='__main__':unittest.main()
