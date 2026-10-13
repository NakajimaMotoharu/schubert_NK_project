"""Distinct cold-profile full ABI after independent recovered whole post."""
import inspect
import json
import pg2305_current_completed_resume_compile as previous
from pg2316_current_cold_resume_sources import sources,TOOLS,CLASS,SOURCE,BOM,BEFORE

TARGET=previous.W/TOOLS


def main():
    post=json.loads((previous.W/'pg2313-current-resume-recovery-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or not post['allClientAdvisoryFlock0']or not post['currentFailedPreparationPairGone']or not post['runtimeWriteReload0']:
        raise ValueError('actual independent recovered fullpost required')
    raw=inspect.getsource(previous.main).replace('pg2305','pg2317').replace('Pg2304','Pg2316')
    namespace={**previous.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TARGET':TARGET}
    exec(compile(inspect.getsource(previous.write),'<newonly cold writer>','exec'),namespace)
    exec(compile(raw,'<current cold six ABI>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
