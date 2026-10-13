"""New-only failed-test reproduction with redacted Throwable types/own frames."""
import inspect
import pg2292_morning_guard_selected as prior


def server():
    return prior.server().replace('PG2292-selected-v1','PG2294-selected-v3')


def main():
    raw=inspect.getsource(prior.prior.main).replace('PG2220','PG2294').replace('pg2220','pg2294').replace('PG2294-selected-v1','PG2294-selected-v3').replace('pg2125-metadata-boundary-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    ns={**prior.prior.__dict__,'FILES':prior.FILES,'SLOT':'pg2294-morning-guard-diagnostic-v3','SERVER':server(),'native_input':prior.native_input}
    exec(compile(raw,'<current failed-test redacted diagnostic>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
