"""New-only actual stage/stop slots after BUG1223; oldfailed2248 immutable, no stop replay."""
import types
import pg2248_newboot_owned_dispatch as prior

GUEST=prior.GUEST
REMOTE='/home/ubuntu/pg2266-fixed-stage-v1'
ARCHIVE='pg2266-'+prior.TOOLS+'.tar'
STAGE=prior.STAGE.replace(prior.ARCHIVE,ARCHIVE).replace(prior.REMOTE,REMOTE)


def run_source():return prior.run_source().replace('pg2248','pg2266')


def run_action(action):
    ns={**prior.prior.prior.runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':prior.PARENT_PREQUAL,'sources':prior.sources,'context':prior.context,'SOURCE':prior.SOURCE,'TOOLS':prior.TOOLS,'BOM':prior.BOM,'POST_SLOT':prior.POST_SLOT,'post_payload':prior.post_payload}
    exec(compile(run_source(),'<corrected newboot new-only owned entry>','exec'),ns);return ns['run_action'](action)


def main():
    fn=types.FunctionType(prior.prior.prior.main.__code__,{**prior.prior.prior.__dict__,'run_action':run_action})
    return fn()


if __name__=='__main__':raise SystemExit(main())
