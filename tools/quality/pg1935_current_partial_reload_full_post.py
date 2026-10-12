"""Separate full post for actual new external reload action; old failed action never reused."""
import inspect
import pg1930_partial_reload_full_post as prior

SLOT='pg1935-current-partial-reload-full-post-v1'


def payload():return prior.payload().replace(prior.SLOT,SLOT)


def main():
    raw=inspect.getsource(prior.main).replace('pg1927-finish-reload','pg1932-finish-reload')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual new current reload full post>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
