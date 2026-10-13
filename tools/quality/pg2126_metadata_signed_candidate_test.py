import copy
import unittest
from pyflakes.api import check
from pg2126_metadata_signed_candidate import CHANGED,validate_gate,verify_delta,main_source

class CandidateContract(unittest.TestCase):
    def gate(self):
        result={'actualExit':0,'productionSource':'a'*40,'tests':3631,'suites':540,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'global100':False,'formalAccepted':False,'semanticChangedClasses':3,'debugOnlyChangedClasses':1,'changedClasses':sorted(CHANGED),'addedClasses':[],'jarHashes':{m:'b'*64 for m in ['protocol','storage','bootstrap','api','web','batch']},'debugLineQualification':{'dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class':{'lineEntries':19,'lineOffset':1,'nonLineBytesIdentical':True}}}
        return {'actualExit':0,'result':result}

    def test_exact_gate_and_each_bad_scalar_or_debug_proof_rejected(self):
        original=self.gate()
        self.assertEqual(original['result'],validate_gate(original,'a'*40))
        for key in ['actualExit','tests','suites','mainClasses','FESFlakyNotRun','staticSixModules','global100','formalAccepted','productionSource','changedClasses','addedClasses','jarHashes','debugLineQualification']:
            value=copy.deepcopy(original);value['result'][key]=None
            with self.subTest(field=key),self.assertRaises(ValueError):validate_gate(value,'a'*40)
        for key,value in [('lineEntries',0),('lineEntries',True),('lineOffset',2),('nonLineBytesIdentical',False)]:
            changed=copy.deepcopy(original);next(iter(changed['result']['debugLineQualification'].values()))[key]=value
            with self.assertRaises(ValueError):validate_gate(changed,'a'*40)

    def test_exact_physical_delta_not_only_logical_class_count(self):
        before={m:{}for m in ['protocol','storage','bootstrap','api','web','batch']}
        before['batch']={n.split(':',1)[1]:'old'for n in CHANGED}
        before['protocol']={str(i):'same'for i in range(1639)}
        after=copy.deepcopy(before)
        for n in after['batch']:after['batch'][n]='new'
        self.assertEqual(1643,verify_delta(before,after))
        after['protocol']['0']='foreign'
        with self.assertRaises(ValueError):verify_delta(before,after)
        after['protocol']['0']='same';after['batch'][next(iter(after['batch']))]='old'
        with self.assertRaises(ValueError):verify_delta(before,after)

    def test_actual_signing_entry_has_current_release_and_no_unit_rewrite(self):
        raw=main_source()
        context='import os,subprocess,json,hashlib,shutil,datetime\nfrom pathlib import Path\nfrom pg2126_metadata_signed_candidate import W,P,T,OLD,OLD_SOURCE,OLD_BOM,NEXT,FROZEN,SIG,validate_gate,verify_delta,receive\nfrom pg1638_api_signed_candidate import require,sha,artifacts,MODULES,class_inventory\nPRODUCTION="fixed"\n__file__="fixed"\n'
        self.assertEqual(0,check(context+raw,'<actual host signing entry context>'))
        self.assertIn('PG2126',raw)
        self.assertIn('PG1846',raw)
        self.assertIn("{'VERSION', 'operations/batch.jar'} <= changed",raw)
        self.assertNotIn('unit_vector',raw)
        self.assertNotIn('PG1638',raw)

if __name__=='__main__':unittest.main()
