"""Data-only actual cohort binding and refusal matrix; no owned-stop authority."""
import copy
import unittest
from pg696_stop_binding import generate
from pg696_compile import source as compiler
from pg696_native_stop import source as transport


def fixture():
    units={u:{'MainPID':str(i+2000000),'InvocationID':str(i+1).zfill(32),'ActiveState':'active','SubState':'running'}for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}
    return {'actualExit':0,'productionSource':'9bd50536f692610036a0ed8b83e0a8b35fe2a66f','batchRun':'8633b77f-77dc-4a78-88b4-41165f159b43','cutoff':'2026-10-09T00:43:10.150245Z','activation':'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee','beforeSha256':'1'*64,'genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':120900000000},'parentEndedUTC':'2026-10-09T01:10:00.000000Z','ownedUnits':units}


class BindingTest(unittest.TestCase):
    def test_compile_and_transport_exact_new_slots(self):
        for raw in (compiler(),transport()):
            compile(raw,'<new transport>','exec')
            for text in ('pg696-native-tools-v1','pg693-completed-readonly-v1','pg696_stop_binding','Pg696NativeStop'):
                self.assertIn(text,raw)
            for text in ('pg642-native-stop-v1','pg640-completed-readonly-v1','Pg642NativeStop'):
                self.assertNotIn(text,raw)
        self.assertIn('pg680-owner-six-host-v1',compiler());self.assertIn('pg682-release-v1',compiler())
        self.assertIn('pg694-chr-a01-native-v1.exit',transport());self.assertIn('/releases/0.1.0-PG682',transport())

    def test_fresh_genuine_fields_and_every_foreign_proof(self):
        proof=fixture();files=generate(proof)
        self.assertIn('Pg696NativeStop.java',files)
        for name,raw in files.items():
            if name.endswith('.py'):compile(raw,'<new actual stop>','exec')
            for old in ('Pg642NativeStop','pg640-completed-readonly-v1','e49243d5','103062293730','0.1.0-PG631'):
                self.assertNotIn(old,raw)
        self.assertIn('119288459330',files['pg696_parent_receipt.py'])
        self.assertIn('pg685-completed-activate-v1',files['pg696_native_refs.py'])
        for key,value in (('batchRun','601297d0-a8ba-47da-852b-0ffeae409965'),('productionSource','0'*40),('actualExit',1),('actualExit',False),('cutoff','2026-10-09T00:43:10.150246Z'),('activation','ad15ac4a-8d8e-4970-bcb3-2e000050ce77')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.subTest(key=key),self.assertRaises(AssertionError):generate(bad)
        for key in ('genuinePid1StartDone','genuineRootDone'):
            bad=copy.deepcopy(proof);bad['genuineCompletion'][key]=False
            with self.subTest(key=key),self.assertRaises(ValueError):generate(bad)


if __name__=='__main__':unittest.main()
