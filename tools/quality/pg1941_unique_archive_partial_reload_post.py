"""Separate full post joined only to actual new unique-archive reload action."""
import inspect
import pg1930_partial_reload_full_post as prior

SLOT='pg1941-unique-archive-partial-reload-full-post-v1'


def payload():return prior.payload().replace(prior.SLOT,SLOT)


def main():
    raw=inspect.getsource(prior.main).replace('pg1927-finish-reload','pg1938-finish-reload')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual unique archive reload post>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
