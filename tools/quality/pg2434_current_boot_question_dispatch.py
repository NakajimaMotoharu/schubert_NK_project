"""Fixed real archive/TOOLS/boot stage and place, new action slots only."""
import types
import pg2414_question_unused_dispatch as prior
from pg2432_current_boot_question_sources import sources,bind,TOOLS,REMOTE
from pg2433_current_boot_question_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE)


def source():return bind(prior.source()).replace('pg2413-frozen','pg2433-frozen')


def runtime_namespace(candidate,before):
    return {**prior.runtime_namespace(candidate,before),'__file__':__file__,'TARGET':TARGET,
            'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources}


def main():
    namespace={**prior.__dict__,'runtime_namespace':runtime_namespace,'source':source}
    function=types.FunctionType(prior.main.__code__,namespace)
    return function()


if __name__=='__main__':raise SystemExit(main())
