"""Strict eleven readiness tests, same qualified Main dependencies; four test-only diff."""
import pg1409_batch_qualified_dependency_selected_v4 as previous

CHANGED=sorted(previous.previous.previous.previous.CHANGED+[
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisRoleReadinessClientTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadinessTest.java'])
SUITES={'dev.codex.schubert.nk.batch.platform.MorningServiceReadinessTest':7,'dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest':4}

def source():
    raw=previous.source().replace('pg1409','pg1414').replace('PG1409','PG1414')
    old='-Dtest=BatchRunRepositoryTest,BackupProfileTest'
    if raw.count(old)!=1:raise ValueError('one strict selected target required')
    raw=raw.replace(old,'-Dtest=MorningServiceReadinessTest,ArtemisRoleReadinessClientTest')
    raw=raw.replace("'requiredSelectedTestCount':24","'requiredSelectedTestCount':11")
    compile(raw,'<strict readiness eleven fixed selection>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.previous.previous.__dict__,fresh_xml=previous.previous.previous.fresh_xml,dependency_goals=previous.previous.dependency_goals,GOALS=previous.previous.GOALS,CHANGED=CHANGED,SUITES=SUITES)
    exec(compile(source(),'<new readiness selected execution>','exec'),env)
    raise SystemExit(env['main']())
