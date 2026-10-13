"""New-only corrected fixture attempt; original compile failure remains untouched."""
import inspect
import pg2292_morning_guard_selected as prior


def server():
    # Suite/Test IDs stay PT-MDB2292; only new output/transfer namespace advances.
    return prior.server().replace('PG2292-selected-v1','PG2293-selected-v2')


def main():
    raw=inspect.getsource(prior.prior.main).replace('PG2220','PG2293').replace('pg2220','pg2293').replace('PG2293-selected-v1','PG2293-selected-v2').replace('pg2125-metadata-boundary-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    ns={**prior.prior.__dict__,'FILES':prior.FILES,'SLOT':'pg2293-morning-guard-selected-v2','SERVER':server(),'native_input':prior.native_input}
    exec(compile(raw,'<new corrected current Morning guard selection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
