"""Distinct verification-only action/namespace, no old reload replay."""
import pg2332_current_existing_runtime_finish_dispatch as previous
from pg2350_current_runtime_verification_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2351_current_runtime_verification_compile import TARGET

REMOTE='/home/ubuntu/pg2352-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous.STAGE).replace('pg2332','pg2352')


def source():
    raw=bind(previous.source()).replace('pg2332','pg2352').replace('pg2331-frozen','pg2351-frozen')
    old="'normalSingleRuntimeReload':action=='verify-runtime'and r.returncode==0,'freshResumeRuntimePrepared':action=='verify-runtime'and r.returncode==0"
    if raw.count(old)!=1:raise ValueError('one verification outcome boundary required')
    return raw.replace(old,"'normalSingleRuntimeReload':False,'verificationOnlyNormalScope':action=='verify-runtime'and r.returncode==0,'freshResumeRuntimePrepared':False")


def main():
    base=previous.previous.previous.template.prior.prior.prior.prior
    ns={**base.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'CANDIDATE':SOURCE,'BOM':BOM}
    exec(compile(source(),'<verification-only current stage entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
