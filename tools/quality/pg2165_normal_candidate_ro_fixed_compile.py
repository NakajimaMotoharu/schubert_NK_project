"""New-only exact candidate-before role compiler after BUG1215 recovery."""
import inspect
import pg2153_normal_candidate_ro_compile as prior
from pg2164_normal_candidate_ro_fixed_sources import sources,TOOLS,bind

TARGET=prior.prior.W/TOOLS


def compiler():return bind(prior.compiler()).replace('pg2153-','pg2165-')


def main():
    ns={**prior.prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,'CANDIDATE':prior.production(),'OLD':prior.CURRENT,'BEFORE':prior.BEFORE}
    exec(compile(inspect.getsource(prior.prior.write),'<new-only role-fixed canonical writer>','exec'),ns)
    exec(compile(compiler(),'<whole role-fixed RO compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
