"""New run for formatted exact same API5 semantics; no old result reuse."""
import inspect
import pg1714_api_configuration_negative_selected as prior


def server():
    raw=prior.server().replace('PG1714-selected-v1','PG1716-selected-v1')
    compile(raw,'<formatted-source isolated five>','exec')
    return raw


def main():
    raw=inspect.getsource(prior.main)
    raw=raw.replace("('PG1628','PG1714'),('pg1628','pg1714')", "('PG1628','PG1716'),('pg1628','pg1716')")
    raw=raw.replace('pg1714-api-configuration-negative-selected-v1','pg1716-formatted-api-configuration-selected-v1')
    ns={**prior.__dict__,'server':server}
    exec(compile(raw,'<formatted-source new-only isolated transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
