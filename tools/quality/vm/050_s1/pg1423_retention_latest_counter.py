"""Same Main independent counters with new retention exec; latest native only."""
import pg1415_readiness_latest_counter as previous
from pg1422_retention_selected import CHANGED

def source():
    raw=previous.source()
    raw=raw.replace("old=W/'pg1411-latest-closing-counter-v1'","old=W/'pg1415-readiness-latest-counter-v1'")
    raw=raw.replace('91e1e36911378b6e450408e5294fb57158029a82180dc468edbabf9972bd7cc0','7005cc3fa899a8996e3c96bac646ae9ba9c22cbac6b8b301fb866c3e749baf29')
    raw=raw.replace("fresh=W/'pg1414-batch-boundary-selected-v1'","fresh=W/'pg1422-batch-boundary-selected-v1'")
    raw=raw.replace("==11 and all(v['failures']","==10 and all(v['failures']")
    marker="require(sha(fresh/'selected.exec')==new['execSha256']);data.append(fresh/'selected.exec');require(len(data)==17"
    if raw.count(marker)!=1:raise ValueError('one exact preserved readiness plus new retention input required')
    raw=raw.replace(marker,"ready=W/'pg1414-batch-boundary-selected-v1/selected.exec';require(sha(ready)==prior['selectedExecSha256']);data.append(ready);require(sha(fresh/'selected.exec')==new['execSha256']);data.append(fresh/'selected.exec');require(len(data)==18")
    raw=raw.replace("'dev/codex/schubert/nk/batch/platform/MorningServiceReadiness','dev/codex/schubert/nk/batch/mq/ArtemisRoleReadinessClient'","'dev/codex/schubert/nk/batch/file/MorningBackupRetention',")
    raw=raw.replace('require(len(closed)==2)','require(len(closed)==1)')
    raw=raw.replace("'totalExecInputs':17","'totalExecInputs':18").replace("'freshSelectedTests':11,'newTestMethods':2","'freshSelectedTests':10,'newTestMethods':1")
    raw=raw.replace("'gainVs1411'","'gainVs1415'")
    raw=raw.replace('pg1415-readiness-latest-counter-v1','pg1423-retention-latest-counter-v1').replace('PG1415-readiness-latest-counter-v1','PG1423-retention-latest-counter-v1')
    raw=raw.replace("old=W/'pg1423-retention-latest-counter-v1'","old=W/'pg1415-readiness-latest-counter-v1'")
    compile(raw,'<full eighteen latest-only retained graph>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.__dict__,CHANGED=CHANGED)
    exec(compile(source(),'<new retention counter>','exec'),env)
    raise SystemExit(env['main']())
