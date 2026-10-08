"""New genuine proof boundaries and old stop reissue guards; no actions."""
import copy
import unittest
from pg655_stop_binding import generate
from pg655_compile import source as compiler
from pg655_native_stop import source as transport


def fixture():
    units={u:{'MainPID':str(i+2000000),'InvocationID':str(i+1).zfill(32),'ActiveState':'active','SubState':'running'}for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}
    return {'actualExit':0,'productionSource':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5','batchRun':'601297d0-a8ba-47da-852b-0ffeae409965','cutoff':'2026-10-08T21:33:23.332578Z','activation':'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee','beforeSha256':'1'*64,'genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':109500000000},'parentEndedUTC':'2026-10-08T22:00:00.000000Z','ownedUnits':units}


class Binding(unittest.TestCase):
    def test_transport_compiler_pins_genuine_and_current_a01_not_old_slots(self):
        for raw in (compiler(),transport()):
            compile(raw,'<new immutable stop binding>','exec')
            for text in ('pg655-native-tools-v1','pg653-completed-readonly-v1','pg655_stop_binding','Pg655NativeStop'):
                self.assertIn(text,raw)
            for text in ('pg642-native-stop-v1','pg640-completed-readonly-v1','Pg642NativeStop'):
                self.assertNotIn(text,raw)
        self.assertIn('pg654-chr-a01-native-v1.exit',transport())

    def test_exact_new_generation_original_seal_and_ordered_stop_protocol(self):
        proof=fixture();files=generate(proof)
        self.assertIn('Pg655NativeStop.java',files)
        for name,raw in files.items():
            if name.endswith('.py'):compile(raw,'<new owned stop>','exec')
            for old in ('Pg642NativeStop','pg640-completed-readonly-v1','e49243d5','7d381b67','103062293730'):
                self.assertNotIn(old,raw)
        java=files['Pg655NativeStop.java']
        for text in ('601297d0-a8ba-47da-852b-0ffeae409965','2026-10-08T21:33:23.332578Z','Pg655NativeStop','genuineParentDone=true'):
            self.assertIn(text,java)
        self.assertIn('107901545407',files['pg655_parent_receipt.py'])
        for key,value in (('batchRun','e49243d5-de84-4714-8612-6912ddc17e9e'),('productionSource','0'*40),('actualExit',1),('activation','7d381b67-b37b-48c6-99ac-e04a336f887d')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.subTest(key=key),self.assertRaises(AssertionError):generate(bad)


if __name__=='__main__':unittest.main()
