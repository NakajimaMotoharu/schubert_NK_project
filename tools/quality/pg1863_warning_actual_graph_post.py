"""Separate current and candidate whole post for actual graph profile."""
import inspect
import pg1859_warning_nested_unused_post as prior
from pg1860_warning_actual_graph_sources import bind

SLOT='pg1863-warning-unused-independent-post-v1'


def payload(post):return bind(prior.payload(post)).replace(prior.SLOT,SLOT)


def main():
    ns={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(bind(inspect.getsource(prior.prior.main)),'<actual graph separate whole post>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
