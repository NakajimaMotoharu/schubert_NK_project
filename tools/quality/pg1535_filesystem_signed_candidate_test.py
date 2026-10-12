"""Independent candidate admission expectations and fixed receive-only transport."""
import unittest
from unittest.mock import patch
import pg1535_filesystem_signed_candidate as target

class GateTest(unittest.TestCase):
    def fixture(self):
        return {'actualExit':0,'result':{'actualExit':0,'productionSource':'4d6bcbddb417b76d27e52d5d9640752c300edccf','tests':3583,'suites':524,'mainClasses':1637,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'formalAccepted':False,'jarHashes':{m:'a'*64 for m in ['protocol','storage','bootstrap','api','web','batch']},'debugLineQualification':{'dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy'+n+'.class':{'lineEntries':2,'lineOffset':1,'nonLineBytesIdentical':True}for n in ['$Metadata','$Snapshot']}}}

    def test_exact_gate_only(self):
        v=self.fixture();self.assertIs(target.validate_gate(v),v['result'])

    def test_each_count_source_quality_and_bool_type_refused(self):
        changes={'actualExit':1,'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','tests':3582,'suites':523,'mainClasses':1635,'FESFlakyNotRun':1,'staticSixModules':1,'classifierFourCounters100':False,'formalAccepted':True}
        for k,value in changes.items():
            for bad in [value,None]:
                with self.subTest(key=k,value=bad):
                    v=self.fixture();v['result'][k]=bad
                    with self.assertRaises(ValueError):target.validate_gate(v)
        v=self.fixture();v['result']['tests']=True
        with self.assertRaises(ValueError):target.validate_gate(v)

    def test_missing_foreign_or_invalid_artifact_hash(self):
        for mode in ['missing','foreign','invalid','null']:
            v=self.fixture();h=v['result']['jarHashes']
            if mode=='missing':del h['api']
            elif mode=='foreign':h['extra']='a'*64
            elif mode=='invalid':h['web']='G'*64
            else:h['batch']=None
            with self.assertRaises(ValueError):target.validate_gate(v)
        for v in [None,{}, {'actualExit':1,'result':self.fixture()['result']}]:
            with self.assertRaises(ValueError):target.validate_gate(v)

    def test_unknown_transfer_rejected_before_authentication(self):
        with patch.object(target,'pinned_key') as key:
            for m in ['../api','web;cat',None,'bootstrap/other']:
                with self.assertRaises(ValueError):target.receive(m)
            key.assert_not_called()

    def test_debug_proof_cannot_hide_semantic_delta(self):
        for mode in ['missing','foreign','zero','offset','changedCode']:
            v=self.fixture();d=v['result']['debugLineQualification'];name=next(iter(d))
            if mode=='missing':del d[name]
            elif mode=='foreign':d['Foreign.class']=d[name]
            elif mode=='zero':d[name]['lineEntries']=0
            elif mode=='offset':d[name]['lineOffset']=2
            else:d[name]['nonLineBytesIdentical']=False
            with self.assertRaises(ValueError):target.validate_gate(v)

if __name__=='__main__':unittest.main()
