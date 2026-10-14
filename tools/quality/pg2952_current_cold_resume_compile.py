"""Current coarse-clock cold source ABI/golden, new-only output; no guest mutations."""
import inspect
import pg2944_current_resume_compile as prior
from pg2950_current_cold_resume_sources import sources,TOOLS,CLASS,SOURCE,BOM,BEFORE

TARGET=prior.prior.W/TOOLS


def main():
    raw=prior.source().replace('pg2944','pg2952').replace('Pg2942','Pg2950')
    ns={**prior.prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TARGET':TARGET}
    exec(compile(inspect.getsource(prior.prior.write),'<current cold immutable source writer>','exec'),ns)
    exec(compile(raw,'<current coarse cold six ABI phases>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
