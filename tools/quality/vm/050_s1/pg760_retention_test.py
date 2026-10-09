"""Independent fixed SQL/Backup vectors at534; mutation matrix and current identity."""
import types
import unittest
from pg692_retention_test import R
from pg760_retention_sources import oracle,capture,bind
from pg662_sources import replace


def suite():
    from pg692_retention_test import replace as old_replace
    # Capture the earlier literal fixture compiler without invoking its test/VM main.
    raw=(R/'pg692_retention_test.py').read_text()
    raw=raw[:raw.index("if __name__=='__main__'")]
    raw=raw.replace('from pg692_retention_sources import oracle,capture,replace','')
    # Reuse its independent literal corpus, substituting new history/attempts before load.
    original=(R/'pg652_retention_test.py').read_text()
    start=raw.index("raw=replace(raw,("); end=raw.index('    env={}',start)
    snippet=raw[start:end]
    env={'replace':old_replace}
    # The generated function expects raw to be local; bind literal input explicitly.
    function='def transform():\n    raw=ORIGINAL\n    '+snippet.replace('\n','\n    ')+'\n    return raw'
    env['ORIGINAL']=original;exec(compile(function,'<literal fixture transform>','exec'),env)
    fixture=env['transform']()
    fixture=replace(fixture, (
        ('new=copy.deepcopy(old)',"old['schubert.batch_runs'] +=[dict(id=515+i,run_id='8633b77f-77dc-4a78-88b4-41165f159b43',step=s,status='SUCCESS'if i<2 else'SKIPPED',business_date='2026-10-09',attempt=5 if i<2 else 4)for i,s in enumerate(STEPS)]\n    new=copy.deepcopy(old)"),
        ('id=515+i,run_id=run','id=525+i,run_id=run'),
        ('attempt=5 if backup else 4','attempt=6 if backup else 5'),
        ("{'id':515,'attempt':5","{'id':525,'attempt':6"),
        ("{'id':516,'attempt':5","{'id':526,'attempt':6"),
        ("a[1]['schubert.batch_runs'][-1]['attempt']=5","a[1]['schubert.batch_runs'][-1]['attempt']=6"),
        ('==524','==534'),('<=524','<=534'),
    ))
    fixture=replace(fixture,(
        ('new=copy.deepcopy(old)',"old['schubert.batch_runs'] +=[dict(id=525+i,run_id='55ac70e7-0180-4c32-8c91-5a379ebedf24',step=s,status='SUCCESS'if i<2 else'SKIPPED',business_date='2026-10-09',attempt=6 if i<2 else 5)for i,s in enumerate(STEPS)]\n    new=copy.deepcopy(old)"),
        ('id=525+i,run_id=run','id=535+i,run_id=run'),('attempt=6 if backup else 5','attempt=7 if backup else 6'),
        ("{'id':525,'attempt':6","{'id':535,'attempt':7"),("{'id':526,'attempt':6","{'id':536,'attempt':7"),
        ("a[1]['schubert.batch_runs'][-1]['attempt']=6","a[1]['schubert.batch_runs'][-1]['attempt']=7"),
        ('==534','==544'),('<=534','<=544'),
    ))
    # The earlier fixture's expectations are still literal PG690, not PG722.
    fixture=replace(fixture,(('2146618','2797579'),('6b3dd954959c43c1bbac2164ec9d0c6b','e4093109ab234700b61dd45711126e4e'),
        ('119288459330','137240785885'),('pg690-fresh-parent-v1','pg758-fresh-parent-v1'),
        ('pg692-retention-post-v1','pg760-retention-post-v1')))
    fixture=bind(fixture)
    namespace={};exec(compile(oracle(),'<current independent oracle>','exec'),namespace)
    mod=types.ModuleType('current_literal_retention');mod.__file__=str(R/'pg760_retention_test.py')
    mod.__dict__.update({k:namespace[k]for k in ('validate','STEPS','ROOT')});mod.payload=capture
    exec(compile(fixture,'<literal524 plus10>','exec'),mod.__dict__)
    return unittest.defaultTestLoader.loadTestsFromTestCase(mod.Retention)


if __name__=='__main__':
    result=unittest.TextTestRunner().run(suite());assert result.testsRun==3
    raise SystemExit(0 if result.wasSuccessful()else 1)
