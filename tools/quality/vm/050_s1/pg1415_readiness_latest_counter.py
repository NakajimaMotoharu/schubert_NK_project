"""One new selected exec joins latest-only current evidence; reuses unchanged monotonic proof."""
import inspect
import pg1411_latest_closing_counter as previous
from pg1414_readiness_selected import CHANGED

def source():
    raw=inspect.getsource(previous.main)
    raw=raw.replace("old=W/'pg1410-batch-selected-same-main-counter-v1'","old=W/'pg1411-latest-closing-counter-v1'")
    raw=raw.replace('e935faf3d347d5598aeaf53f53b2599e3184c0718aedcbc6e3d3cccc2aed3813','91e1e36911378b6e450408e5294fb57158029a82180dc468edbabf9972bd7cc0')
    raw=raw.replace("sha(admin/'manifest.safe.json')==prior['previousNativeManifestSha256']and sha(selected/'manifest.safe.json')==prior['selectedManifestSha256']", "sha(admin/'manifest.safe.json')=='c05911e9ddbf292c2375d155166fc8602bcc41345de47a15e8b7f723efdd1502'and sha(selected/'manifest.safe.json')=='6fe5deb4c97ec31066fd4eac6091ddc8323acbb30478255c46a241c5c6ff981b'")
    start=raw.index("    cp=':'.join(libraries);start=")
    end=raw.index("    modules=('protocol'",start)
    raw=raw[:start]+"""    cp=':'.join(libraries);start=datetime.datetime.now(datetime.timezone.utc)
    require(not subprocess.check_output(['git','diff','--name-only','5c5f345240fa0453a227d7c3bb5457ede5e918a7','--',str(R/'NativeClosingSelect1411.java'),str(R/'NativeClosingSelect1411Test.java')]))
    proof=prior['closingOracle'];require(proof['sameSession']is True and proof['probeMonotonic']is True and proof['latestClosingOnly']is True)
    fresh=W/'pg1414-batch-boundary-selected-v1';new=json.loads((fresh/'manifest.safe.json').read_bytes())
    require(new['actualExit']==0 and new['productionMainSource']==SOURCE and new['staticIssues']==0 and new['allBatchMainClassBytesEqual1279']is True and new['freshXmlRequired']is True and new['notRunCount']==0)
    require(sum(v['tests']for v in new['testCounts'].values())==11 and all(v['failures']==v['errors']==v['skipped']==0 for v in new['testCounts'].values()))
    for path,digest in new['sourceHashes'].items():require(sha(T/path)==digest)
"""+raw[end:]
    raw=raw.replace("require(len(data)==16 and", "require(len(data)==16 and")
    marker="    helper=W/'pg571-current-ten-native-v2/classes';"
    if raw.count(marker)!=1:raise ValueError('one exact input scope extension required')
    raw=raw.replace(marker,"    require(sha(fresh/'selected.exec')==new['execSha256']);data.append(fresh/'selected.exec');require(len(data)==17 and admin/'bootstrap-0.exec'not in data)\n"+marker)
    raw=raw.replace("    require(counters==prior['moduleCounters'])", "    kinds=('LINE','METHOD','CLASS','BRANCH');remaining={k:sum(v[k]['missed']for v in counters.values())for k in kinds};gain={k:prior['remaining'][k]-remaining[k]for k in kinds};require(all(v>=0 for v in gain.values()))")
    raw=raw.replace("'dev/codex/schubert/nk/batch/repository/BatchRunRepository','dev/codex/schubert/nk/batch/backup/BackupProfile'", "'dev/codex/schubert/nk/batch/platform/MorningServiceReadiness','dev/codex/schubert/nk/batch/mq/ArtemisRoleReadinessClient'")
    raw=raw.replace("'oracleLogSha256':sha(run/'oracle.private.log'),'actualMonotonicLogSha256':sha(run/'actual-monotonic.private.log')", "'monotonicProofReusedFrom':'PG1411','monotonicProofSourceManifestSha256':sha(old/'manifest.safe.json')")
    raw=raw.replace("'allSixCountersEqualPriorUnionDiagnostic':True", "'allSixCountersEqualPriorUnionDiagnostic':False,'gainVs1411':gain")
    raw=raw.replace("'remaining':prior['remaining']", "'remaining':remaining").replace("'totalExecInputs':16", "'totalExecInputs':17").replace("'freshSelectedTests':24,'newTestMethods':3", "'freshSelectedTests':11,'newTestMethods':2")
    raw=raw.replace("'selectedExecSha256':s['execSha256']", "'selectedExecSha256':new['execSha256'],'previousSelectedExecSha256':s['execSha256']")
    raw=raw.replace('pg1411-latest-closing-counter-v1','pg1415-readiness-latest-counter-v1').replace('PG1411-latest-closing-counter-v1','PG1415-readiness-latest-counter-v1')
    raw=raw.replace("old=W/'pg1415-readiness-latest-counter-v1'", "old=W/'pg1411-latest-closing-counter-v1'")
    raw=raw.replace("'allSixCountersEqualPriorUnionDiagnostic','remaining'", "'gainVs1411','remaining'")
    compile(raw,'<qualified same Main readiness latest-only counter>','exec');return raw

if __name__=='__main__':
    env=dict(previous.__dict__,CHANGED=CHANGED)
    exec(compile(source(),'<new readiness counter input graph>','exec'),env)
    raise SystemExit(env['main']())
