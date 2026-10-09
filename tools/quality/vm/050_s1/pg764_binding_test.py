"""Literal data-only current proof and each unknown refusal, no VM authority."""
import copy
import unittest
from pg764_stop_binding import generate
from pg764_compile import source as compiler
from pg764_native_stop import source as transport
from pg765_terminal_final import source as post


def fixture():
    units={u:{'MainPID':str(i+3000000),'InvocationID':str(i+10).zfill(32),'ActiveState':'active','SubState':'running'} for i,u in enumerate(('caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'))}
    return {'actualExit':0,'productionSource':'8d4b68b4f1449932ebe506aaf08e584bbfea8dd2',
            'batchRun':'9de2d03c-28c7-4647-97d9-c66ace06048c','cutoff':'2026-10-09T05:42:22.532331Z',
            'activation':'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee','beforeSha256':'1'*64,
            'genuineCompletion':{'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':138900000000},
            'parentEndedUTC':'2026-10-09T06:05:00.000000Z','ownedUnits':units}


class BindingTest(unittest.TestCase):
    def test_compile_transport_and_post_new_source(self):
        for raw in (compiler(),transport(),post()):
            compile(raw,'<new current protocol>','exec')
            for text in ('pg764','pg761-completed-readonly-v1'):
                self.assertIn(text,raw)
            for old in ('pg696','pg693','Pg696'):
                self.assertNotIn(old,raw)
        self.assertIn('pg748-closing-six-host-v1',compiler()); self.assertIn('pg750-release-v1',compiler())
        self.assertIn('pg762-chr-a01-native-v1.exit',transport()); self.assertIn('0.1.0-PG750',transport())
        self.assertIn('pg750-manifest.sig',post())

    def test_actual_genuine_tuple_and_each_foreign(self):
        proof=fixture();files=generate(proof)
        self.assertIn('Pg764NativeStop.java',files)
        for name,raw in files.items():
            if name.endswith('.py'):compile(raw,'<current ownedstop refs>','exec')
            for old in ('Pg696','pg693-completed-readonly-v1','8633b77f','119288459330','PG682'):
                self.assertNotIn(old,raw)
        self.assertIn('137240785885',files['pg764_parent_receipt.py'])
        self.assertIn('pg752-completed-activate-v1',files['pg764_native_refs.py'])
        for key,value in (('batchRun','8633b77f-77dc-4a78-88b4-41165f159b43'),('productionSource','0'*40),('actualExit',1),('actualExit',False),('cutoff','2026-10-09T05:42:22.532332Z'),('activation','ab8895ca-4fb1-440d-b174-bc9f1f27505a')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.assertRaises(AssertionError):generate(bad)
        for key in ('genuinePid1StartDone','genuineRootDone'):
            bad=copy.deepcopy(proof);bad['genuineCompletion'][key]=False
            with self.assertRaises(ValueError):generate(bad)
        for badend in (137240785884,139040785886,None,True):
            bad=copy.deepcopy(proof);bad['genuineCompletion']['endMonotonicUs']=badend
            with self.assertRaises(AssertionError):generate(bad)


if __name__=='__main__':unittest.main()
