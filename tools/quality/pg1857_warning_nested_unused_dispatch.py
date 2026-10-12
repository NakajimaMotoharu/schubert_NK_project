"""New-only nested ABI direct stage/place after BUG1181; old partial slots untouched."""
import inspect
import pg1851_warning_signed_unused_dispatch as prior
from pg1855_warning_nested_unused_sources import sources,TOOLS,REMOTE,bind
from pg1856_warning_nested_unused_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE)


def source():return bind(prior.source()).replace('pg1850-frozen','pg1856-frozen')


def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'TARGET':TARGET,'GUEST':GUEST,'STAGE':STAGE,'REMOTE':REMOTE,'sources':sources,'source':source}
    exec(compile(raw,'<new-only direct nested stage/place transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
