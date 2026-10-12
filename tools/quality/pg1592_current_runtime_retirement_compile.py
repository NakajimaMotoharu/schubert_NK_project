"""Freeze actual current-only retirement ABI and exact full refs before any mutation."""
import pg1580_current_owned_stop_compile as prior
from pg1591_current_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS

def main():
    raw=prior.compiler_source().replace('Pg1579','Pg1591').replace('pg1580','pg1592')
    raw=raw.replace("'genuineParentBeforeSha256':BEFORE","'completedBeforeSha256':BEFORE")
    env={**prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':SHA,'TARGET':prior.prior.W/TOOLS}
    exec(compile(raw,'<current exact finite retirement compiler>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
