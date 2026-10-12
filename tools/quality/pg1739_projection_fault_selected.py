"""Fresh selected7 after actual JDBC/provider-fault additions; not old6 reuse."""
import inspect
import pg1737_successful_backup_projection_selected as prior

SLOT='pg1739-successful-backup-fault-selected-v1'

def server():
    raw=prior.server().replace('PG1737','PG1739').replace('Pg1737SuccessfulProjectionLauncher','Pg1739ProjectionFaultLauncher')
    for a,b in [('tests6','tests7'),("=='6'","=='7'"),('==6)','==7)'),("'tests':6","'tests':7")]:raw=raw.replace(a,b)
    compile(raw,'<fresh projection7 with allowed provider failures>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('PG1737','PG1739').replace('pg1737','pg1739')
    files=[s.replace('Pg1737SuccessfulProjectionLauncher','Pg1739ProjectionFaultLauncher')for s in prior.FILES]
    ns={**prior.__dict__,'FILES':files,'SLOT':SLOT,'server':server}
    exec(compile(raw,'<fresh projection7 transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
