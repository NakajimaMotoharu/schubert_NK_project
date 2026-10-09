"""REC856002..004: independent field/sequence/no-intent and failed-owned fault fixtures."""
import ast,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
import pg856_sources as p
R=Path(__file__).resolve().parent
def namespace():
    h=types.ModuleType('pg856_owned');h.__file__=str(R/'pg856_owned.py')
    with patch.dict(sys.modules,{'dbus':types.SimpleNamespace()}):exec(compile(p.helper(),'<856 exact helper>','exec'),h.__dict__)
    return h
class Test(unittest.TestCase):
    def test_exact_cohort_and_no_intent_operation(self):
        h=namespace();self.assertEqual(18,len(h.FIELDS));self.assertEqual(32,len(h.FIELDS_CONFIGURATION))
        self.assertEqual(('3506798','eeb1b35ca3214176adae5d45bb6432ab',17241379),h.EXPECTED['schubert-nk-api.service'])
        self.assertEqual(('3507964','8c46100f289f47b9a24d2c12bd443ba2',17242685),h.EXPECTED['schubert-nk-web.service'])
        self.assertIn('289e9efc63292bbf1d4a0e952bf98b98bca390550b3a41b492288dd1bdfe0fb5',p.helper())
        j=p.java();self.assertNotIn('PairEvidence',j);self.assertNotIn('quarantinePair',j);self.assertNotIn('retirePair',j)
        self.assertIn('validateCohort(epoch,permit,startup)',j);self.assertIn('37356ff23d0393924c22079bd4c87fce7c3070155d84704fb1cb143e7b1c60a5',j)
        self.assertLess(j.index('helper("terminal")'),j.index('files.revoke(invalid,permit)'))
        self.assertLess(j.index('files.revoke(invalid,permit)'),j.index('helper("retired")'))
        self.assertLess(j.index('refs.release();'),j.index('db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE"'))
        for stale in ('PG750','PG796','rows()==554','3417355L+','active().isPresent()'):self.assertNotIn(stale,j)
        ast.parse(p.helper())
    def test_canonical_epoch_rejects_foreign_state_generation_and_fields(self):
        h=namespace();raw=('NKEPOCH1\nstate=ISSUED\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=8b153538-1523-4987-a456-6cbea0d345ee\nrun_id=9de2d03c-28c7-4647-97d9-c66ace06048c\ncutoff_utc=2026-10-09T05:42:22.532331Z\nactivation_id=021111b4-6de5-4733-917d-5ac176240ffc\npermit_sha256='+'a'*64+'\n').encode()
        self.assertTrue(h.epoch_value(raw,False));self.assertFalse(h.epoch_value(raw,True))
        invalid=raw.replace(b'state=ISSUED',b'state=INVALID').replace(b'a'*64,b'-')
        self.assertTrue(h.epoch_value(invalid,True));self.assertFalse(h.epoch_value(invalid,False))
        for bad in (raw[:-1],raw+b'other=x\n',raw+b'state=ISSUED\n',raw.replace(b'8b153538-1523-4987-a456-6cbea0d345ee',b'0eece14c-f832-47c2-b7dd-14125682e7ea'),None,b'\xff\n'):
            self.assertFalse(h.epoch_value(bad,False))
    def test_independent_fixed_stop_faults(self):
        # Reuse the independently authored fixed fault vectors, not production-generated expected.
        import pg813_sources as old
        import pg778_sources as first
        raw=first.bind((R/'pg496_timeout_owned_test.py').read_text()).replace('Pg778','Pg779').replace('PG778','PG779').replace('pg778','pg779')
        raw=p.bind(old.bind(raw)).replace('e9f11f1c-f087-458a-aad0-8c1e4e140571',p.EPOCH)
        pairs=[('4113865','3509997'),('b656fdfe067a4cb8a542708750af019c','87dd86b0f2c243198a05ae36903fdefa'),('25667027','17244888'),('4108080','3507964'),('1dedba9e9ee648fb94eca6232385e018','8c46100f289f47b9a24d2c12bd443ba2'),('25663790','17242685'),('4105598','3506798'),('730085ab1173444b83c9bf2c8127c94e','eeb1b35ca3214176adae5d45bb6432ab'),('25662174','17241379'),('3939714','3427249'),('12360e619aa7445684692c59badc7c51','9a576ea327854479a3196fe41b2c0a61'),('25552139','17151412')]
        for a,b in pairs:raw=raw.replace(a,b)
        # The original import may be rebound by old.bind; require one declared helper import.
        raw=raw.replace('import pg856_timeout_owned as h','import pg856_owned as h')
        self.assertIn('import pg856_owned as h',raw)
        with patch.dict(sys.modules,{'pg856_owned':namespace()}):exec(compile(raw,'<856 independent owned stop fault>','exec'),{'__name__':'literal_oracle'})
if __name__=='__main__':unittest.main()
