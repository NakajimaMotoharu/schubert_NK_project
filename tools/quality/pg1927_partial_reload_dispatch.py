"""Direct stage/finish-reload only; source pins and real preownership producer."""
import inspect
import pg1880_warning_publication_dispatch as prior
from pg1925_disjoint_role_partial_reload_sources import sources,TOOLS,CLASS
from pg1926_disjoint_role_partial_reload_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1927-fixed-stage-v1'
STAGE=prior.STAGE.replace('pg1880-fixed-stage-v1','pg1927-fixed-stage-v1').replace('pg1877-warning-publication-tools-v1',TOOLS)


def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1877','pg1925'),('Pg1877','Pg1925'),('PG1877','PG1925'),('pg1879-frozen','pg1926-frozen'),('pg1880-','pg1927-'),('activate','finish-reload')]:raw=raw.replace(old,new)
    raw=raw.replace("fixed['productionSource']!=OLD","fixed['productionSource']!=CANDIDATE")
    raw=raw.replace("'Pg1925TransitionTest',",'')
    raw=raw.replace('PG1638','PG1846')
    raw=raw.replace("'installedBeforeSource':OLD","'installedBeforeSource':CANDIDATE")
    start=raw.index('    changed=False if')
    end=raw.index("    with Path(str(base)+'.safe.json')",start)
    raw=raw[:start]+"""    value={**begin,'actualExit':r.returncode,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completedObservedHead':observed,'sourceQualified':r.returncode==0 and observed==operator,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'currentApprovalEpochChanged':False,'unitExchangeAndReload':False,'normalSingleReload':action=='finish-reload'and r.returncode==0,'startsStopsSqlWrites0':True,'oldFailedNormalized':False}
"""+raw[end:]
    compile(raw,'<actual reload-only direct entry>','exec');return raw


def main():
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<current approved one reload direct entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
