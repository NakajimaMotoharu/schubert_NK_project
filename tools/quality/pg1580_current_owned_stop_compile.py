"""Freeze qualified stop ABI against actual PG1544, with actual constructor tests."""
import pg1248_fresh_owned_stop_compile as prior
from pg1254_fresh_owned_stop_compile_v2 import source as original_compiler
from pg1579_current_owned_stop_sources import sources,SOURCE,BEFORE,TOOLS

def compiler_source():
    raw=original_compiler()
    for old,new in [('Pg1253','Pg1579'),('pg1254','pg1580'),('pg1068-release-v1','pg1544-release-v1')]:
        if old not in raw:raise ValueError('qualified current compiler binding absent')
        raw=raw.replace(old,new)
    compile(raw,'<current stop ABI qualification>','exec');return raw

def main():
    env={**prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':BEFORE,'TARGET':prior.W/TOOLS}
    exec(compile(compiler_source(),'<current stop ABI compiler>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
