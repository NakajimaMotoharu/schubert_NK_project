"""Generate secret-free679 manifest from independently qualified actual records."""
import hashlib
import json
import os
from pathlib import Path
from pg1446_current_cold_stage import W
from pg1700_new_source_live_binding import SOURCE

OUT=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/output/679_manifest.json'
RECORDS={
    'start':'pg1699-new-current-ordinary-once-v1/manifest.safe.json',
    'live':'pg1700-new-source-live-binding-v1.safe.json',
    'done':'pg1701-new-source-done-receipt-v1.safe.json',
    'seal':'pg1702-new-source-completed-seal-v1/manifest.safe.json',
    'compiler':'pg1704-frozen-v1.safe.json',
    'stage':'pg1705-stage-v1.safe.json',
    'preflight':'pg1706-new-source-stop-preflight-v1/manifest.safe.json',
    'stop':'pg1705-stop-v1.safe.json',
    'post':'pg1707-new-source-terminal-post-v1.safe.json',
    'catalog':'pg1708-new-source-native-catalog-v1/manifest.safe.json',
    'native':'pg1709-new-source-native-qualified-v1/manifest.safe.json',
}


def main():
    os.umask(0o077);records={};hashes={}
    for name,relative in RECORDS.items():
        raw=(W/relative).read_bytes();value=json.loads(raw)
        if type(value.get('actualExit'))is not int or value['actualExit']!=0:raise ValueError('actual successful evidence required')
        records[name]=value;hashes[name]={'path':relative,'sha256':hashlib.sha256(raw).hexdigest()}
    for name in RECORDS.keys()-{'start','done','preflight'}:
        if records[name].get('productionSource')!=SOURCE:raise ValueError('same Main source required')
    if records['done'].get('source')!=SOURCE or records['preflight'].get('productionSource')!=SOURCE:raise ValueError('same receipt source required')
    result=records['native']['result']
    if (result['productionSource']!=SOURCE or result['classByteMismatch']!=0
            or result['qualified1633Tests']!=3596 or result['currentNativeStreams']!=8
            or result['oldNativeImported']is not False or records['post']['allClientAdvisoryFlock0']is not True):
        raise ValueError('sameSource native and all-resource qualification required')
    remaining={k:sum(m[k]['missed']for m in result['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}
    value={'program':'NK-OPS-001','testIds':['PT-OPS-LIVE-1700-001','PT-OPS-DONE-1701-001','PT-OPS-SQL-1702-001','PT-OPS-STOP-1705-001','PT-OPS-POST-1707-001','PT-OPS-NATIVE-1709-001'],
           'productionSource':SOURCE,'testSource':'1683dd9f6de00e71d2317d9af3cd50400a37bf4e','fullSnapshot':'0044e7d8d1ce46040ec4e8092f63902bd7b32512',
           'records':hashes,'rootElapsedSeconds':records['done']['receipt']['elapsedSeconds'],'originalBudgetSeconds':1800,
           'doneUtc':records['seal']['doneEndUtc'],'sqlOracle':records['seal']['businessOracle'],
           'ownedExplicitStops':4,'terminalReceipts':8,'resourcePostExit':0,'privateAfterSha256':records['post']['proofHashes']['after.private.json']['sha256'],
           'nativeStreams':8,'oldNativeFourteenPreservedNotImported':True,'classByteMismatch':0,'remainingMissed':remaining,
           'serverNativeManifestSha256':records['native']['manifestSha256'],'coverage100':result['coverage100'],
           'bugRefs':['BUG-1155'],'yktRefs':['YKT-923'],'ssRefs':['SS341','SS343','SS353','SSC274','SSC275'],
           'formalAccepted':False,'wholeLeafAcceptedDelta':0,'effortCompletionRate':None,
           'classification':'PROVISIONAL_SAME_SOURCE_NATIVE_NOT_451_COMPLETE','backupContentRetentionPending':True,
           'commands':['pg1700 readonly','pg1701 readonly','pg1702 readonly','pg1704 Werror/oracles','pg1706 preflight','pg1705 stage once','pg1705 stop once under management_gate','pg1707 readonly','pg1708 readonly','pg1709 sameSource CRC/coverage'],
           'rawCredentialTokenSessionMasterDumpIncluded':False}
    with OUT.open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'output':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'coverage100':value['coverage100'],'formalAccepted':False}))


if __name__=='__main__':main()
