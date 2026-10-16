"""Publish genuine current Root/Browser/ownedstop/native safe metadata, no private snapshots."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg3798_hygiene_current_observer import SOURCE,BOM

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3838-hygiene-current-lifecycle-v1'
RECEIPTS=[('PT-CURRENT-ROOT-3808','pg3808-hygiene-current-terminal-v1/manifest.safe.json'),('PT-CURRENT-ROWS-3810','pg3810-hygiene-current-rows-v1/manifest.safe.json'),('PT-CURRENT-SEAL-3812','pg3812-hygiene-current-full-seal-v1/manifest.safe.json'),('PT-CURRENT-BROWSER-3814','pg3814-hygiene-browser-business-actual-v1/manifest.safe.json'),('PT-CURRENT-COMPOSITE-3816','pg3816-hygiene-browser-composite-full-seal-v1/manifest.safe.json'),('PT-CURRENT-PARENT18-3818','pg3818-hygiene-parent-projection-v1.safe.json'),('PT-CURRENT-OWNEDSTOP-3826','pg3826-stop-v1.safe.json'),('PT-CURRENT-OWNEDPOST-3828','pg3828-hygiene-owned-post-v1/manifest.safe.json')]


def main():
    inputs=[]
    for test,name in RECEIPTS:
        raw=(W/name).read_bytes();value=json.loads(raw)
        if type(value.get('actualExit'))is not int or value['actualExit']!=0 or value.get('productionSource',value.get('source'))!=SOURCE:raise ValueError('genuine current0 safe receipt required')
        # These specific receipt schemas contain metadata/counts/hashes only;
        # never read their private evidence files or raw rows.
        if any(k in value for k in ['rows','password','token','cookie','sessionId','payloadCiphertext']):raise ValueError('private data cannot be published')
        inputs.append((test,{**value,'testId':test,'originalReceiptSha256':hashlib.sha256(raw).hexdigest(),'originalReceipt':name}))
    qualified=json.loads((W/'pg3832-hygiene-native-qualified-v1/manifest.safe.json').read_bytes());native=qualified['result']
    if qualified['actualExit']!=0 or native['productionSource']!=SOURCE or native['classByteMismatch']!=0 or native['currentNativeStreams']!=9 or native['validatedNativePoints']!=10 or native['oldNativeImported']:raise ValueError('newsource physical CRC/session qualification required')
    OUT.mkdir();files={}
    def write(name,value):
        raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode();(OUT/name).write_bytes(raw);files[name]=hashlib.sha256(raw).hexdigest()
    for index,(test,value)in enumerate(inputs,1):write(f'{index:03d}-receipt.json',value)
    write('current-native-counters.json',{k:native[k]for k in ['productionSource','run','currentNativeStreams','validatedNativePoints','classByteMismatch','oldNativeImported','hostOnlyCounters','moduleLocalCounters','moduleCounters','gain','xmlHashes','coverage100','formalAccepted','wholeNativeAccepted']})
    write('current-native-gaps.json',native['gaps'])
    write('current-native-session-hashes.json',native['currentNativeSessions'])
    missed={k:sum(v[k]['missed']for v in native['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}
    value={'run':'PG3838-hygiene-current-lifecycle-v1','source':SOURCE,'BOM':BOM,'formalAccepted':False,'tests':3714,'suites':545,'physicalMainClasses':1643,'RootGenuineWarning10':True,'RootElapsedSeconds':1758.747101,'originalBudgetSeconds':1800,'actualBrowserPassed':12,'ordinaryOwnedStops':4,'whole24IndependentOracle':True,'newsourceNativePoints':10,'newsourceNativeStreams':9,'nativeClassByteMismatch':0,'historicalNativeImported':False,'nativeQualificationReceiptSha256':hashlib.sha256((W/'pg3832-hygiene-native-qualified-v1/manifest.safe.json').read_bytes()).hexdigest(),'serverNativeManifestSha256':qualified['manifestSha256'],'remaining':missed,'coverage100':False,'rawPrivateDataExported':False,'unaccepted':['Backup manifest/retention full oracle','Answer provider acceptance','remaining same-source resume/legacy branches','F03','all four counters100','CHR including QA051 final','451 fullgate/trace/handoff'],'formalReference':'PT-WEB-20260925-24/1964PT/53scope','historicalIndividualAccepted':17,'individualScope':190,'wholeEffortCompletionRate':None,'files':files}
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode();(OUT/'manifest.json').write_bytes(raw);print(json.dumps({'files':len(files),'manifestSha256':hashlib.sha256(raw).hexdigest(),'remaining':missed,'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
