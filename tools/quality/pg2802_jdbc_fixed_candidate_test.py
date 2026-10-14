"""Pure tool guards only: no signature, key read, VM or production PT credit."""
import copy
import unittest
from pyflakes.api import check
import pg2802_jdbc_fixed_signed_candidate as candidate
import pg2800_jdbc_null_fixed_full_qualified as qualified


class JdbcCandidateGuards(unittest.TestCase):
    def gate(self):
        name='dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class'
        return {'actualExit':0,'result':{'actualExit':0,'productionSource':candidate.SOURCE,
            'tests':3680,'suites':542,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,
            'classifierFourCounters100':True,'global100':False,'formalAccepted':False,
            'semanticChangedClasses':None,'debugOnlyChangedClasses':1,
            'changedClasses':sorted(candidate.PHYSICAL),'addedClasses':[],
            'debugLineQualification':{name:{'lineEntries':70,'lineOffset':1,'nonLineBytesIdentical':True}},
            'jarHashes':{m:'a'*64 for m in candidate.prior.MODULES}}}

    def test_fresh_all_scope_gate_rejects_old_or_incomplete_results(self):
        value=self.gate();self.assertEqual(value['result'],candidate.validate_gate(value,candidate.SOURCE))
        for key,bad in [('tests',3673),('suites',541),('productionSource',candidate.OLD_SOURCE),
                        ('staticSixModules',1),('FESFlakyNotRun',1),('mainClasses',1642),
                        ('global100',True),('formalAccepted',True),('semanticChangedClasses',6),
                        ('addedClasses',['foreign']),('changedClasses',sorted(candidate.PHYSICAL)[:-1])]:
            with self.subTest(key=key):
                wrong=copy.deepcopy(value);wrong['result'][key]=bad
                with self.assertRaises(ValueError):candidate.validate_gate(wrong,candidate.SOURCE)
        wrong=copy.deepcopy(value);wrong['actualExit']=False
        with self.assertRaises(ValueError):candidate.validate_gate(wrong,candidate.SOURCE)

    def test_exact_three_main_delta_and_all1643_inventory(self):
        before={m:{}for m in candidate.prior.MODULES}
        for i in range(1643):before['batch'][str(i)+'.class']='a'*64
        for i,name in enumerate(sorted(candidate.DELTA)):
            before['batch'][name.split(':',1)[1]]=before['batch'].pop(str(i)+'.class')
        after=copy.deepcopy(before)
        for name in candidate.DELTA:after['batch'][name.split(':',1)[1]]='b'*64
        self.assertEqual(1643,candidate.verify_delta(before,after))
        wrong=copy.deepcopy(after);wrong['batch']['3.class']='b'*64
        with self.assertRaises(ValueError):candidate.verify_delta(before,wrong)
        with self.assertRaises(ValueError):candidate.verify_delta(before,before)
        wrong=copy.deepcopy(after);wrong['batch']['foreign.class']='b'*64
        with self.assertRaises(ValueError):candidate.verify_delta(before,wrong)

    def test_complete_namespaces_fixed_roles_no_lifecycle(self):
        raw=candidate.main_source()
        supplied='\n'.join(k+'=None'for k in {**candidate.prior.__dict__,'qualify_source':None}if k.isidentifier()and k!='main')
        self.assertEqual(0,check(supplied+'\n'+raw,'<host signing whole namespace>'))
        self.assertEqual(0,check(qualified.server(),'<whole independent XML namespace>'))
        for marker in ['PG2802','PG2654','3680','542','pg2800-jdbc-null-fixed-full-qualified-v1','qualify_source()']:
            self.assertIn(marker,raw)
        for forbidden in ['daemon-reload','systemctl','Root/noargs']:
            self.assertNotIn(forbidden,raw)
        self.assertIn("require(morning_prefix+'$Rows.class'in changed)",qualified.server())


if __name__=='__main__':unittest.main()
