"""Fixed direct stage/place entry, full closure/hash/gate; no publication or reload."""
import json
import sys
import pg1683_closed_unused_dispatch as prior
from pg1848_warning_signed_unused_sources import sources,TOOLS,REMOTE,ARCHIVE
from pg1850_warning_signed_unused_compile import TARGET
from pg1844_warning_unit_full_six import CANDIDATE
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS


def profile(raw):
    raw=raw.replace('PG1638','__NEW_RELEASE__').replace('PG1544','PG1638').replace('__NEW_RELEASE__','PG1846')
    for old,new in [('pg1638-manifest','pg1846-manifest'),('pg1681-completed-unused-tools-v4',TOOLS),('pg1683-release-v4.tar',ARCHIVE),('pg1683-fixed-stage-v1','pg1851-fixed-stage-v1'),('PG1683','PG1851'),('pg1683','pg1851'),('pg1682-frozen-v1','pg1850-frozen-v1'),('pg1675-remaining-owner-full-post-v1','pg1849-warning-completed-current-before-v1'),('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',CANDIDATE),('Pg1640','Pg1848'),('pg1640','pg1848'),('Pg1660','Pg1848'),('Pg1681','Pg1848'),('pg1681','pg1848')]:raw=raw.replace(old,new)
    return raw


STAGE=profile(prior.STAGE)


def source():
    raw=profile(prior.source())
    marker="    safe={**begin,'actualExit':code,"
    if raw.count(marker)!=1:raise ValueError('one direct source provenance boundary required')
    raw=raw.replace(marker,"    completed_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()\n"+marker)
    raw=raw.replace("'oldFailedNormalized':False}","'oldFailedNormalized':False,'completedObservedHead':completed_head,'operatorSourceUnchanged':completed_head==begin['operatorSource'],'sourceQualified':code==0 and completed_head==begin['operatorSource']}")
    compile(raw,'<same direct unused signed candidate profile>','exec');return raw


def main():
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('fixed stage/place only')
    candidate=json.loads((W/'pg1846-candidate-build-v1.safe.json').read_bytes());before=json.loads((W/'pg1849-warning-completed-current-before-v1/manifest.safe.json').read_bytes())
    if candidate['actualExit']!=0 or candidate['candidateSource']!=CANDIDATE or before['actualExit']!=0:raise ValueError('actual signed candidate/current proof required')
    ns=prior.namespace(candidate)
    ns.update(TARGET=TARGET,GUEST=GUEST,REMOTE=REMOTE,STAGE=STAGE,SOURCE=CANDIDATE,DIGEST=candidate['manifestSha256'],BASELINE_SHA=before['privateBeforeSha256'],sources=lambda bom:sources(bom,before['privateBeforeSha256']))
    exec(compile(source(),'<actual immutable direct stage/place entry>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
