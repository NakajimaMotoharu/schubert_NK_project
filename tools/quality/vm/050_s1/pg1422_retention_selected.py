"""Ten selected retention contracts, same Main/dependency bytes and fresh XML only."""
import pg1414_readiness_selected as previous

CHANGED=sorted(previous.CHANGED+['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupRetentionTest.java'])
SUITES={'dev.codex.schubert.nk.batch.file.MorningBackupRetentionTest':10}

def source():
    raw=previous.source().replace('pg1414','pg1422').replace('PG1414','PG1422')
    old='-Dtest=MorningServiceReadinessTest,ArtemisRoleReadinessClientTest'
    if raw.count(old)!=1:raise ValueError('one strict retention selection required')
    raw=raw.replace(old,'-Dtest=MorningBackupRetentionTest').replace("'requiredSelectedTestCount':11","'requiredSelectedTestCount':10")
    compile(raw,'<fixed retention selection>','exec');return raw

if __name__=='__main__':
    base=previous.previous.previous.previous.previous.__dict__
    env=dict(base,fresh_xml=previous.previous.previous.previous.fresh_xml,dependency_goals=previous.previous.previous.dependency_goals,GOALS=previous.previous.previous.GOALS,CHANGED=CHANGED,SUITES=SUITES)
    exec(compile(source(),'<new retention selected execution>','exec'),env)
    raise SystemExit(env['main']())
