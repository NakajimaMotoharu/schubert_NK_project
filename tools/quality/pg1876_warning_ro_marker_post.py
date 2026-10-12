"""Separate current/hostRO whole post for matched literal producer slot."""
import inspect
import pg1871_warning_candidate_ro_post as prior
from pg1872_warning_ro_marker_sources import bind

SLOT='pg1876-warning-candidate-ro-post-v1'


def payload(post):return bind(prior.payload(post)).replace(prior.SLOT,SLOT)


def main():
    raw=inspect.getsource(prior.prior.main).replace('pg1865-place-v1.safe.json','pg1875-prepare-ro-v1.safe.json')
    ns={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<literal-matched RO separate post>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
