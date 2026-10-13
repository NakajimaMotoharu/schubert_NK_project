"""Direct new action/archive/root, actual producer gate before M/A/DB/Refs."""
import pg1938_unique_archive_partial_reload_dispatch as prior
from pg1980_fresh_completed_resume_sources import sources,TOOLS,CLASS
from pg1982_fresh_completed_resume_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1983-fixed-stage-v1'
STAGE=prior.STAGE.replace('pg1938-fixed-stage-v1','pg1983-fixed-stage-v1').replace('pg1938-qualified-tools-v1.tar','pg1983-qualified-tools-v1.tar').replace('pg1925-partial-reload-tools-v1',TOOLS)


def source():
    raw=prior.source().replace('pg1938-','pg1983-').replace('pg1925','pg1980').replace('Pg1925PartialReload',CLASS).replace('Pg1925','Pg1980').replace('PG1925','PG1980').replace('pg1926-frozen','pg1982-frozen').replace('finish-reload','prepare-resume')
    raw=raw.replace("'normalSingleReload':action=='prepare-resume'and r.returncode==0","'normalSingleReload':False,'normalSingleRuntimeReload':action=='prepare-resume'and r.returncode==0,'freshResumeRuntimePrepared':action=='prepare-resume'and r.returncode==0")
    compile(raw,'<actual freshresume direct dispatch>','exec');return raw


def main():
    original=prior.prior.prior
    ns={**original.prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<actual freshresume entry namespace>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
