"""Freeze current seventeen-file exact retirement ABI; no VM mutation."""
import inspect
import pg2031_fresh_normal_warning_stop_compile as prior
from pg2050_fresh_completed_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS


def context():return SHA,None,None,None


def main():
    raw=inspect.getsource(prior.main).replace('Pg2030','Pg2050').replace('pg2031','pg2051')
    # The shared compiler labels the before digest; keep its established field name.
    ns={**prior.__dict__,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS}
    exec(compile(raw,'<current exact retirement ABI compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
