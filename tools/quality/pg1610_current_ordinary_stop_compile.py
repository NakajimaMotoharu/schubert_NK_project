"""Freeze current ordinary stop helpers; no Unit operation."""
import pg1580_current_owned_stop_compile as prior
from pg1609_current_ordinary_owned_stop_sources import sources,SOURCE,BEFORE,TOOLS

def compiler_source():
    return prior.compiler_source().replace('1579','1609').replace('1580','1610')

def main():
    env={**prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':BEFORE,'TARGET':prior.prior.W/TOOLS}
    exec(compile(compiler_source(),'<ordinary stop helper qualification>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
