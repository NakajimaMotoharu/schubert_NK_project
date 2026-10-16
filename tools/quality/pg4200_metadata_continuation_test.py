"""Independent fixed receipt/retainer fixtures and emitted operation topology; no VM access."""
import ast
import copy
import unittest
from pyflakes.api import check
import pg4200_metadata_continuation as p


class ContinuationTest(unittest.TestCase):
    def test_transport255_is_not_guest_or_success_and_requires_separate_terminal(self):
        r={'actualExit':255,'oldParentNormal':False,'formalAccepted':False,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':'5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3'}
        t={'allOldPidsGone':True,'allOldFlocksAdvisory0':True,'old4152Normal':False,'oldCloseNormal':False}
        self.assertIs(True,p.failed_transport(r,t))
        for key in r:
            with self.subTest(missing=key),self.assertRaises(ValueError):p.failed_transport({k:v for k,v in r.items()if k!=key},t)
        for status in [0,143,True,None,'255']:
            with self.subTest(status=status),self.assertRaises(ValueError):p.failed_transport({**r,'actualExit':status},t)
        for key in t:
            with self.subTest(terminal=key),self.assertRaises(ValueError):p.failed_transport(r,{**t,key:not t[key]})

    def fixture(self):
        return {'pid':791348,'ticks':14602179,'argvSha256':'172536db0a293878cb1780e85aa687b825c625a75a9d95fec914ecdf608d1520','children':[],
                'cgroup':'0::/user.slice/user-1000.slice/session-930.scope\n',
                'authority':{'PPid':'791346','Uid':'0 0 0 0','Gid':'0 0 0 0','Groups':'0','NoNewPrivs':'0','CapInh':'0000000000000000','CapAmb':'0000000000000000','CapBnd':'000001ffffffffff','CapEff':'000001ffffffffff','CapPrm':'000001ffffffffff'},
                'fds':{str(i):{'target':name,'metadata':[16,100+i,0,0,4480,1,0,0,0],'fdinfo':'fixture'+str(i)}for i,name in enumerate(['pipe:[12618427]','pipe:[12618428]','pipe:[12618429]','/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0','socket:[12616611]'])}}

    def test_full_five_fd_and_authority_contract_no_extra_or_mutated_descriptor(self):
        old=self.fixture();self.assertIs(True,p.same_retainer(old,copy.deepcopy(old)))
        for key in old:
            now=copy.deepcopy(old);now.pop(key)
            with self.subTest(missing=key),self.assertRaises(ValueError):p.same_retainer(old,now)
        for fd in old['fds']:
            for field in old['fds'][fd]:
                now=copy.deepcopy(old);now['fds'][fd][field]=None
                with self.subTest(fd=fd,field=field),self.assertRaises(ValueError):p.same_retainer(old,now)
        for key in old['authority']:
            now=copy.deepcopy(old);now['authority'][key]='different'
            with self.subTest(authority=key),self.assertRaises(ValueError):p.same_retainer(old,now)
        for key,val in [('pid',1),('ticks',1),('argvSha256','other'),('children',[1]),('cgroup','other')]:
            wrong={**old,key:val}
            with self.subTest(fixed=key),self.assertRaises(ValueError):p.same_retainer(wrong,wrong)

    def test_one_fixed_term_and_unchanged_partial_post_no_business_replay(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<continuation>'))
        tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([(791348,14602179)],[(c.args[0].value,c.args[1].value)for c in calls])
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Name)and n.id=='pg_terminate_backend'for n in ast.walk(tree)))
        self.assertFalse("'systemctl','stop'"in p.BODY)
        self.assertIn("job('partial.py','inspect','partial-inspect')",raw)
        self.assertIn("job('partial.py','recover','partial-recover')",raw)
        self.assertIn("job('post.py',None,'independent-post')",raw)
        self.assertTrue("except OSError:pass\n  while True:time.sleep(1)"in p.BODY)


if __name__=='__main__':unittest.main()
