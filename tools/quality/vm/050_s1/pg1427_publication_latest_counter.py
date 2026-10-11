"""Latest-only nineteen inputs; explicitly partial publication native contract."""
import pg1423_retention_latest_counter as previous
from pg1426_publication_factory_selected import CHANGED

def source():
    raw=previous.source()
    raw=raw.replace("old=W/'pg1415-readiness-latest-counter-v1'","old=W/'pg1423-retention-latest-counter-v1'")
    raw=raw.replace('7005cc3fa899a8996e3c96bac646ae9ba9c22cbac6b8b301fb866c3e749baf29','cb72dcf285b181092aa9a05394645b198494f72b315457dbc461e55d8a24ceab')
    raw=raw.replace("fresh=W/'pg1422-batch-boundary-selected-v1'","fresh=W/'pg1426-batch-boundary-selected-v1'")
    raw=raw.replace("==10 and all(v['failures']","==7 and all(v['failures']")
    raw=raw.replace("require(sha(ready)==prior['selectedExecSha256'])","require(sha(ready)=='d23a0692754b0d676874320063d55fdf52fe97cd0a16567ee949bf1e53380b59')")
    marker="require(sha(fresh/'selected.exec')==new['execSha256']);data.append(fresh/'selected.exec');require(len(data)==18"
    if raw.count(marker)!=1:raise ValueError('one exact preserved retention input required')
    raw=raw.replace(marker,"retention=W/'pg1422-batch-boundary-selected-v1/selected.exec';require(sha(retention)==prior['selectedExecSha256']);data.append(retention);require(sha(fresh/'selected.exec')==new['execSha256']);data.append(fresh/'selected.exec');require(len(data)==19")
    raw=raw.replace('dev/codex/schubert/nk/batch/file/MorningBackupRetention','dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication')
    raw=raw.replace("require(all(counts[k]==0 for k in kinds))","require({k:counts[k]for k in kinds}=={'LINE':1,'METHOD':1,'CLASS':0,'BRANCH':0})")
    raw=raw.replace("'newCounterClosedClasses'","'observedPartialClasses'").replace("'gainVs1415'","'gainVs1423'")
    raw=raw.replace("'totalExecInputs':18","'totalExecInputs':19").replace("'freshSelectedTests':10,'newTestMethods':1","'freshSelectedTests':7,'newTestMethods':1")
    raw=raw.replace('pg1423-retention-latest-counter-v1','pg1427-publication-latest-counter-v1').replace('PG1423-retention-latest-counter-v1','PG1427-publication-latest-counter-v1')
    raw=raw.replace("old=W/'pg1427-publication-latest-counter-v1'","old=W/'pg1423-retention-latest-counter-v1'")
    compile(raw,'<fixed nineteen partial publication graph>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.previous.__dict__,CHANGED=CHANGED)
    exec(compile(source(),'<new publication counter>','exec'),env)
    raise SystemExit(env['main']())
