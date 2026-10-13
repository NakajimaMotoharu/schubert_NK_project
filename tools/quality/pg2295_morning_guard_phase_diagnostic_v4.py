"""New-only precondition/phase witness, fixed fixture no provider message output."""
import inspect
import pg2292_morning_guard_selected as prior


def server():
    return prior.server().replace('PG2292-selected-v1','PG2295-selected-v4')


def main():
    raw=inspect.getsource(prior.prior.main).replace('PG2220','PG2295').replace('pg2220','pg2295').replace('PG2295-selected-v1','PG2295-selected-v4').replace('pg2125-metadata-boundary-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    ns={**prior.prior.__dict__,'FILES':prior.FILES,'SLOT':'pg2295-morning-guard-phase-diagnostic-v4','SERVER':server(),'native_input':prior.native_input}
    exec(compile(raw,'<current fixture phase diagnostic>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
