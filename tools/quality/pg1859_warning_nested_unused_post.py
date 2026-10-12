"""Separate current/signed unused187 post for new-only nested placement."""
import inspect
import pg1853_warning_unused_independent_post as prior
from pg1855_warning_nested_unused_sources import bind

SLOT='pg1859-warning-unused-independent-post-v1'


def payload(post):return bind(prior.payload(post)).replace(prior.SLOT,SLOT)


def main():
    raw=bind(inspect.getsource(prior.main))
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new-only nested placement separate whole post>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
