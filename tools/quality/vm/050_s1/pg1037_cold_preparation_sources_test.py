"""Independent full finite-directory literals and actual generated callback wiring."""
import ast
import copy
import stat
import unittest
from pg1026_cold_observation_contract import namespace_layout
from pg1037_cold_preparation_sources import java,guest
from pg1032_cold_handoff_preflight_v5 import missing_globals


class Preparation(unittest.TestCase):
    def fixture(self,prepared):
        entries={'@root':['maintenance.lock','startup-admission.lock','maintenance'],'maintenance':[]}
        meta={'@root':[28,7,0,0,stat.S_IFDIR|0o755,8 if prepared else 3,80,11,12],
              'maintenance':[28,9,0,0,stat.S_IFDIR|0o700,2,40,11,12]}
        if prepared:
            entries['@root']+=['startup','backup-request','cleanup-request','expiry-request','pt-coverage']
            for name in ['startup','backup-request','cleanup-request','expiry-request','pt-coverage']:
                entries[name]=[];meta[name]=[28,8,0,0,stat.S_IFDIR|(0o711 if name=='pt-coverage'else 0o700),8 if name=='pt-coverage'else 2,40,11,12]
            entries['pt-coverage']=['parent','cleanup','expiry','root-api','backup','inspector']
            for name in ['parent','cleanup','expiry','root-api','backup','inspector']:
                owner=(31,41)if name=='backup'else(32,42)if name=='inspector'else(0,0)
                entries['pt-coverage/'+name]=[];meta['pt-coverage/'+name]=[28,9,*owner,stat.S_IFDIR|0o700,2,40,11,12]
        return entries,meta,{'backup':(31,41),'inspector':(32,42)}

    def test_independent_exact_before_and_prepared_layout(self):
        for prepared in (False,True):
            e,m,w=self.fixture(prepared);self.assertIs(True,namespace_layout(e,m,w,prepared))

    def test_half_created_unknown_file_bad_role_permission_and_link_refused(self):
        e,m,w=self.fixture(True)
        for name in m:
            for index,value in ((2,99),(4,stat.S_IFDIR|0o777),(5,99)):
                changed=copy.deepcopy(m);changed[name][index]=value
                with self.assertRaises(ValueError):namespace_layout(e,changed,w,True)
        for name in e:
            changed=copy.deepcopy(e);changed[name].append('foreign')
            with self.assertRaises(ValueError):namespace_layout(changed,m,w,True)
        with self.assertRaises(ValueError):namespace_layout({k:v for k,v in e.items()if k!='startup'},m,w,True)
        for entries,meta,workers,prepared in ((None,m,w,True),(e,None,w,True),(e,m,None,True),(e,m,w,None),(e,m,{'backup':(0,0),'inspector':(32,42)},True)):
            with self.assertRaises(ValueError):namespace_layout(entries,meta,workers,prepared)

    def test_real_profile_uses_byte_auth_before_ro_and_immutable_after(self):
        j=java();g=guest();ast.parse(g)
        self.assertLess(j.index('refs.check("prepare")'),j.index('Pg387TrustedDeployment.freezeCandidate()'))
        self.assertLess(j.index('Pg387TrustedDeployment.freezeCandidate()'),j.index('Pg387TrustedDeployment.verify()'))
        self.assertLess(j.index('Pg387TrustedDeployment.verify()'),j.index('phase="FINITE_EMPTY_NAMESPACES"'))
        self.assertTrue('StartupPermitFiles.invalidate'not in j)
        self.assertTrue('contract.namespace_layout(entries,metas,workers,True)'in g)
        self.assertEqual([],missing_globals(g,['snapshot','complete_configuration','read_pair','parent','controls','runtime_namespaces']))
        self.assertTrue("except BaseException as failure:retain(failure)"in g)


if __name__=='__main__':unittest.main()
