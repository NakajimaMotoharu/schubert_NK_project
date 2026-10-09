"""Literal data-only current proof and each unknown refusal, no VM authority."""
import copy
import unittest
from pg728_stop_binding import generate
from pg728_compile import source as compiler
from pg728_native_stop import source as transport
from pg729_terminal_final import source as post


def fixture():
    units={u:{'MainPID':str(i+3000000),'InvocationID':str(i+10).zfill(32),'ActiveState':'active','SubState':'running'} for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}
    return {'actualExit':0,'productionSource':'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',
            'batchRun':'55ac70e7-0180-4c32-8c91-5a379ebedf24','cutoff':'2026-10-09T03:00:51.014287Z',
            'activation':'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee','beforeSha256':'1'*64,
            'genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':129000000000},
            'parentEndedUTC':'2026-10-09T03:25:00.000000Z','ownedUnits':units}


class BindingTest(unittest.TestCase):
    def test_compile_transport_and_post_new_source(self):
        for raw in (compiler(),transport(),post()):
            compile(raw,'<new current protocol>','exec')
            for text in ('pg728','pg725-completed-readonly-v1'):
                self.assertIn(text,raw)
            for old in ('pg696','pg693','Pg696'):
                self.assertNotIn(old,raw)
        self.assertIn('pg713-expiry-six-host-v1',compiler()); self.assertIn('pg715-release-v1',compiler())
        self.assertIn('pg726-chr-a01-native-v1.exit',transport()); self.assertIn('0.1.0-PG715',transport())
        self.assertIn('pg715-manifest.sig',post())

    def test_actual_genuine_tuple_and_each_foreign(self):
        proof=fixture();files=generate(proof)
        self.assertIn('Pg728NativeStop.java',files)
        for name,raw in files.items():
            if name.endswith('.py'):compile(raw,'<current ownedstop refs>','exec')
            for old in ('Pg696','pg693-completed-readonly-v1','8633b77f','119288459330','PG682'):
                self.assertNotIn(old,raw)
        self.assertIn('127549297774',files['pg728_parent_receipt.py'])
        self.assertIn('pg717-completed-activate-v1',files['pg728_native_refs.py'])
        for key,value in (('batchRun','8633b77f-77dc-4a78-88b4-41165f159b43'),('productionSource','0'*40),('actualExit',1),('actualExit',False),('cutoff','2026-10-09T03:00:51.014288Z'),('activation','c6815985-26c5-4f5f-aed0-abc81fa8f71e')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.assertRaises(AssertionError):generate(bad)
        for key in ('genuinePid1StartDone','genuineRootDone'):
            bad=copy.deepcopy(proof);bad['genuineCompletion'][key]=False
            with self.assertRaises(ValueError):generate(bad)
        for badend in (127549297773,129349297775,None,True):
            bad=copy.deepcopy(proof);bad['genuineCompletion']['endMonotonicUs']=badend
            with self.assertRaises(AssertionError):generate(bad)


if __name__=='__main__':unittest.main()
