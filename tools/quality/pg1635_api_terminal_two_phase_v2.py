"""New-only API two-phase PT after independent literal oracle correction BUG1142."""
import inspect
import pg1634_api_terminal_two_phase as prior


def main():
    raw=inspect.getsource(prior.main).replace('PG1634','PG1635').replace('pg1634','pg1635')
    ns={**prior.__dict__,'server':lambda:prior.server().replace('PG1634','PG1635')}
    exec(compile(raw,'<new-only API independent oracle corrected>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
