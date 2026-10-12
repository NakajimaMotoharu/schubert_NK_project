"""Reserve one exact current canonical runtime retirement; no Root or service stops."""
import pg1581_current_owned_stop_dispatch as prior
from pg1591_current_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=prior.STAGE.replace('pg1581','pg1594').replace('PG1581','PG1594').replace('pg1579-current-owned-stop-tools-v1',TOOLS)

def source():
    raw=prior.source().replace('pg1581','pg1594').replace('Pg1579','Pg1591').replace('pg1579-current-owned-stop-tools-v1',TOOLS).replace('pg1580','pg1592')
    raw=raw.replace('pg1582-current-stop-preflight-v1.safe.json','pg1593-current-retirement-preflight-v1.safe.json')
    raw=raw.replace("(['stage'],['stop'])","(['stage'],['retire'])").replace('stage or stop required','stage or retire required')
    raw=raw.replace('Pg1591NativeStop stop','Pg1591NativeStop retire').replace("frozen['genuineParentBeforeSha256']","frozen['completedBeforeSha256']")
    compile(raw,'<closed once current retirement dispatcher>','exec');return raw

def main():
    env={**prior.prior.previous.previous.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':SHA,'GUEST':GUEST,'STAGE':STAGE}
    exec(compile(source(),'<current immutable exact runtime stage-retire>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
