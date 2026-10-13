"""Extract public parent18 only from the actual immutable current full seal."""
import inspect
import pg2244_newboot_parent_projection as previous

SLOT='pg2372-current-resume-parent-projection-v1'


def payload(sha):
    return previous.payload(sha).replace('pg2242-newboot-fresh-day-full-seal-v1','pg2368-current-resume-full-seal-v1')


def main():
    raw=inspect.getsource(previous.prior.prior.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2368-current-resume-full-seal-v1')
    ns={**previous.prior.prior.__dict__,'SOURCE':previous.prior.SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current fullseal parent projection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
