"""Read-only public parent18 projection from qualified newsource fullseal."""
import inspect
import pg2083_current_newrun_sealed_parent_fields as prior
from pg2176_newsource_normal_observer import SOURCE

SLOT='pg2187-newsource-parent-projection-v1'


def payload(sha):
    raw=prior.payload(sha).replace('pg2081-current-newrun-full-live-seal-v1','pg2186-newsource-full-live-seal-v1').replace('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE)
    return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2186-newsource-full-live-seal-v1')
    ns={**prior.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<newsource sealed parent18 reader>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
