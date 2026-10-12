"""Independent Unit10/sole exception vector, full-source and class-delta negatives."""
import copy
import unittest
from pg1846_warning_unit_signed_candidate import unit_vector,validate_gate,verify_delta,prior,CANDIDATE


class Signed(unittest.TestCase):
    def test_exact_unit_warning_only_and_reject_already_changed(self):
        self.assertEqual(b'# SSC278/BUG1162: completed WARNING10 is normal; all other nonzero exits remain failures.\n[Unit]\n[Service]\nRestart=no\nSuccessExitStatus=10\n',unit_vector(b'[Unit]\n[Service]\nRestart=no\n'))
        for bad in [None,b'',b'Restart=no\n',b'[Unit]\nRestart=no\nSuccessExitStatus=10\n',b'[Unit]\nRestart=no\nRestart=no\n']:
            with self.assertRaises(ValueError):unit_vector(bad)

    def test_full_gate_and_all_main_byte_delta_rejections(self):
        v={'actualExit':0,'productionSource':CANDIDATE,'tests':3618,'suites':536,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'global100':False,'formalAccepted':False,'changedClasses':[],'addedClasses':[],'jarHashes':{m:'a'*64 for m in prior.MODULES}}
        self.assertIs(v,validate_gate({'actualExit':0,'result':v},CANDIDATE))
        for key,bad in [('tests',3596),('tests',True),('productionSource','foreign'),('staticSixModules',1),('changedClasses',['changed']),('jarHashes',{})]:
            x=copy.deepcopy(v);x[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):validate_gate({'actualExit':0,'result':x},CANDIDATE)
        for before,after in [(None,{}),({},{}),({m:{}for m in prior.MODULES},{m:{}for m in prior.MODULES})]:
            with self.assertRaises(ValueError):verify_delta(before,after)


if __name__=='__main__':raise SystemExit(unittest.main())
