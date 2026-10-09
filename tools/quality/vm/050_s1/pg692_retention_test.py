"""Independent old literal vectors augmented with current 514-row history."""
import types
import unittest
from pathlib import Path
from pg692_retention_sources import oracle,capture,replace

R=Path(__file__).resolve().parent


def suite():
    raw=(R/'pg652_retention_test.py').read_text()
    raw=replace(raw,(
        ('from pg652_retention_oracle import validate,STEPS,ROOT',''),('from pg652_capture_retention import payload',''),
        ("old['schubert.batch_runs']+=today;new=copy.deepcopy(old)",
         "old['schubert.batch_runs']+=today\n    old['schubert.batch_runs'] +=[dict(id=505+i,run_id='601297d0-a8ba-47da-852b-0ffeae409965',step=s,status='SUCCESS'if i<2 else'SKIPPED',business_date='2026-10-09',attempt=4 if i<2 else 3)for i,s in enumerate(STEPS)]\n    new=copy.deepcopy(old)"),
        ('id=505+i,run_id=run','id=515+i,run_id=run'),
        ('attempt=4 if backup else 3','attempt=5 if backup else 4'),
        ("{'id':505,'attempt':4", "{'id':515,'attempt':5"),
        ("{'id':506,'attempt':4", "{'id':516,'attempt':5"),
        ('stat.S_IFDIR|0o700,15,100','stat.S_IFDIR|0o700,14,100'),
        ('for i in range(8):','for i in range(7):'),
        ("('old0','old1')", "('old0',)"),
        ("'eligibleUpperBound':8,'maximumEligibleAfterNew':9", "'eligibleUpperBound':7,'maximumEligibleAfterNew':8"),
        ("'expectedRetentionDeletes':2,'expectedDeleted':['old0','old1']", "'expectedRetentionDeletes':1,'expectedDeleted':['old0']"),
        ("result['retentionDeleted'],2", "result['retentionDeleted'],1"),
        ("a[1]['schubert.batch_runs'][-1]['attempt']=4", "a[1]['schubert.batch_runs'][-1]['attempt']=5"),
        ('1826480','2146618'),('095f6d1d7f8442b7b2b44ae59a4314f5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('107901545407','119288459330'),('pg650-fresh-parent-v2','pg690-fresh-parent-v1'),
        ('==514','==524'),('<=514','<=524'),
        ("'pg652-retention-post-v2'", "'pg692-retention-post-v1'"),
    ))
    env={};exec(compile(oracle(),'<independent current rows/byte oracle>','exec'),env)
    mod=types.ModuleType('literal_current_retention');mod.__file__=str(R/'pg692_retention_test.py')
    mod.__dict__.update({k:env[k]for k in ('validate','STEPS','ROOT')});mod.payload=capture
    exec(compile(raw,'<literal current retention vectors>','exec'),mod.__dict__)
    return unittest.defaultTestLoader.loadTestsFromTestCase(mod.Retention)


if __name__=='__main__':
    actual=unittest.TextTestRunner().run(suite());assert actual.testsRun==3
    raise SystemExit(0 if actual.wasSuccessful()else 1)
