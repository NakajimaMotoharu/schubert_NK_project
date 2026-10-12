"""Actual graph qualified new-only stage/place; all older partial freezes retained."""
import inspect
import pg1857_warning_nested_unused_dispatch as prior
from pg1860_warning_actual_graph_sources import sources,TOOLS,REMOTE,bind
from pg1861_warning_actual_graph_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE)


def source():return bind(prior.source()).replace('pg1856-frozen','pg1861-frozen')


def main():
    ns={**prior.prior.__dict__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'source':source}
    exec(compile(inspect.getsource(prior.prior.main),'<actual graph new direct dispatcher>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
