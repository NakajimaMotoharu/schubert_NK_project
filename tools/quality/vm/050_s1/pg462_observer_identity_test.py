"""Independent SS342 literals; no VM/process mutation or fabricated native result."""
import unittest
from pg462_observer_identity import authenticate_ready

class ReadyIdentityTest(unittest.TestCase):
    def setUp(self):
        self.p={'Uid':'999 999 999 999','Gid':'981 981 981 981','Groups':'980 981 982 986','NoNewPrivs':'1',**{k:'0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')}}
        self.info={'commit':'literal-test-source','schema':'027'}
    def call(self,before,after,health=(200,b'{"status":"UP"}'),info=None):
        return authenticate_ready(before,after,health,(200,self.info) if info is None else info,self.info,'999','981',['980','981','982','986'])
    def test_transition_before_ready_is_not_failure_or_success(self):
        root=dict(self.p,Uid='0 0 0 0')
        self.assertFalse(self.call(root,root,(503,b'{"status":"OUT_OF_SERVICE"}')))
        self.assertTrue(self.call(self.p,self.p))
    def test_info_mismatch_or_unknown_health_is_not_ready(self):
        self.assertFalse(self.call({}, {}, info=(200,{'commit':'other'})))
        self.assertFalse(self.call({}, {}, info=(503,self.info)))
        self.assertFalse(self.call({}, {}, (200,b'{"status":"UNKNOWN"}')))
    def test_both_actor_samples_must_have_exact_authority(self):
        for key,value in [('Uid','0 0 0 0'),('Gid','0 0 0 0'),('Groups','981'),('NoNewPrivs','0')]+[(k,'0000000000000001') for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')]:
            bad=dict(self.p,**{key:value})
            for before,after in [(bad,self.p),(self.p,bad)]:
                with self.subTest(key=key):
                    with self.assertRaises(AssertionError):self.call(before,after)
    def test_missing_unknown_null_fields_are_not_ready(self):
        for bad in [{k:v for k,v in self.p.items() if k!='Uid'},dict(self.p,extra='unknown'),dict(self.p,Uid=None)]:
            with self.assertRaises(AssertionError):self.call(bad,self.p)

if __name__=='__main__':unittest.main()
