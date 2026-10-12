"""New-only v4 stage/place, fixed closure names and critical management gate."""
import inspect
import sys
import pg1661_completed_unused_dispatch_v3 as previous
import pg1682_closed_candidate_compile as compiler
from pg1681_closed_candidate_sources import sources, TOOLS, REMOTE
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=previous.STAGE.replace('pg1661','pg1683').replace('PG1661','PG1683').replace('pg1659-completed-unused-tools-v3',TOOLS)


def namespace(candidate):
    ns=previous.namespace(candidate)
    ns.update(TARGET=compiler.TARGET,GUEST=GUEST,REMOTE=REMOTE,STAGE=STAGE,sources=sources)
    return ns


def source():
    raw=previous.source()
    for a,b in [('pg1661','pg1683'),('pg1660-frozen-v1.safe.json','pg1682-frozen-v1.safe.json'),('pg1658-owned-recovery-independent-post-v1/manifest.safe.json','pg1675-remaining-owner-full-post-v1/manifest.safe.json'),('pg1659-completed-unused-tools-v3',TOOLS),('pg1683-release-v3.tar','pg1683-release-v4.tar')]:raw=raw.replace(a,b)
    marker="    generated['pg1640_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle_raw).hexdigest())+'\\n'+generated['pg1640_native_refs.py']"
    if raw.count(marker)!=1:raise ValueError('one frozen input hash source join required')
    raw=raw.replace(marker,"    for name in ['pg1640_native_refs.py','pg1681_input_preflight.py']:\n        generated[name]='BUNDLE_HASH='+repr(hashlib.sha256(bundle_raw).hexdigest())+'\\n'+generated[name]")
    raw=raw.replace("'Pg1660CurrentIdentityTest','Pg1640UnusedStage place'", "'Pg1660CurrentIdentityTest','Pg1681InputBoundaryTest','Pg1640UnusedStage place'")
    compile(raw,'<actual v4 fixed source dispatcher>','exec')
    return raw


def main():
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('closed new stage/place required')
    code=inspect.getsource(previous.previous.main)
    ns={**previous.previous.__dict__,'namespace':namespace,'source':source}
    exec(compile(code,'<new closed input dispatcher transport>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):
        return ns['main']()


if __name__=='__main__':raise SystemExit(main())
