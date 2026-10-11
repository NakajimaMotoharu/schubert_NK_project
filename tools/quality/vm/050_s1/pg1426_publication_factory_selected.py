import pg1422_retention_selected as previous

CHANGED=sorted(previous.CHANGED+['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupRequestPublicationTest.java'])
SUITES={'dev.codex.schubert.nk.batch.file.MorningBackupRequestPublicationTest':7}

def source():
    raw=previous.source().replace('pg1422','pg1426').replace('PG1422','PG1426')
    old='-Dtest=MorningBackupRetentionTest'
    if raw.count(old)!=1:raise ValueError('one strict publication selected suite required')
    raw=raw.replace(old,'-Dtest=MorningBackupRequestPublicationTest').replace("'requiredSelectedTestCount':10","'requiredSelectedTestCount':7")
    compile(raw,'<fixed publication selection>','exec');return raw

if __name__=='__main__':
    base=previous.previous.previous.previous.previous.previous.__dict__
    env=dict(base,fresh_xml=previous.previous.previous.previous.previous.fresh_xml,dependency_goals=previous.previous.previous.previous.dependency_goals,GOALS=previous.previous.previous.previous.GOALS,CHANGED=CHANGED,SUITES=SUITES)
    exec(compile(source(),'<new publication selected execution>','exec'),env)
    raise SystemExit(env['main']())
