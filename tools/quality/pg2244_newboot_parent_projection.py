"""Current immutable fullseal parent18 projection; no old-boot live state substitution."""
import inspect
import pg2187_newsource_parent_projection as prior

SLOT='pg2244-newboot-parent-projection-v1'


def payload(sha):
    return prior.payload(sha).replace('pg2186-newsource-full-live-seal-v1','pg2242-newboot-fresh-day-full-seal-v1')


def main():
    raw=inspect.getsource(prior.prior.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2242-newboot-fresh-day-full-seal-v1')
    ns={**prior.prior.__dict__,'SOURCE':prior.SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current immutable parent18 transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
