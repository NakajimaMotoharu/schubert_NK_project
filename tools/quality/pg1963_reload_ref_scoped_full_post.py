"""Independent full post qualifies all manager fields inside its own ten Ref scope."""
import inspect
import pg1953_reload_recovery_full_post as prior

SLOT='pg1963-reload-ref-scoped-full-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT)
    begin=raw.index("original_configuration=after['configuration'];new_configuration={}")
    end=raw.index("after['configuration']=new_configuration",begin)+len("after['configuration']=new_configuration")
    qualification=raw[begin:end];raw=raw[:begin]+raw[end:]
    marker='    def snapshot():\n'
    if raw.count(marker)!=1:raise ValueError('one real snapshot Ref scope required')
    raw=raw.replace(marker,'\n'.join('    '+line for line in qualification.splitlines())+'\n\n'+marker)
    from pyflakes.api import check
    if check(raw,'<actual Ref scoped full post>'):raise ValueError('all actual post globals required')
    compile(raw,'<current independent tenRef full post>','exec');return raw


def main():
    ns={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    raw=inspect.getsource(prior.prior.main).replace('pg1903-partial-pair-once-handoff-v1','pg1950-reload-pair-once-handoff-v1')
    exec(compile(raw,'<actual new Ref scoped full post entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
