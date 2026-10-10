"""Sanitized current Bootstrap native preservation; no new runtime or acceptance."""
import difflib,hashlib,json,datetime
from pathlib import Path
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def main():
    p=W/'pg992-current-ten-native-v1/manifest.safe.json';m=json.loads(p.read_bytes());assert m['actualExit']==0 and m['productionSource']=='40ef6e894573d2ffab1d1732124960f9c98d5f97'
    post=json.loads((W/'pg989-bootstrap-post-v4.safe.json').read_bytes());assert post['run']=='PG989-bootstrap-post-v4'and post['actualExit']==0 and post['capturedNormal20VerifiedBeforeCurrent']
    counters={}
    for k in ('LINE','METHOD','CLASS','BRANCH'):
        missed=sum(v[k]['missed']for v in m['moduleCounters'].values());covered=sum(v[k]['covered']for v in m['moduleCounters'].values());counters[k]={'missed':missed,'covered':covered,'total':missed+covered,'percent':round(covered*100/(covered+missed),2)}
    proof={'source':m['productionSource'],'run':'PG978-v2/983/985/986/989-v4/992','state':'CURRENT_BOOTSTRAP_EXIT20_POST_NATIVE10_QUALIFIED_NOT_GLOBAL','actualExit':0,'sameSourceHost':'PG926/927','tests':3560,'suites':523,'staticModules0':6,'bootstrapUnitSeconds':1.52426,'bootstrapExpectedExit':20,'bootstrapToolExecuteSeconds':14.241175,'currentNativeStreams':10,'distinctJvmExecutions':9,'distinctOsProcessCount':None,'incrementalVsCurrentNative8':m['incrementalVsPG972'],'remaining':m['remaining'],'counters':counters,'otherSourceNativeImported':0,'wholeAccepted':False,'formalAcceptedDelta':0,'N':None,'T':None,'evidence':'evidence/01_PT/018_NK-OPS-001/621_当40ef_Bootstrap既存ADMIN・Inspector_仕様経過.md'}
    public={'schemaVersion':1,**proof,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','operatorSource':m['operatorSource'],'command':'python3 -B tools/quality/vm/050_s1/pg992_current_bootstrap_native_counter.py','jdk':'25.0.4','osVersion':None,'osVersionNote':'not freshly measured in this operation','input':'Qualified current40ef8 only + two immutable Bootstrap dumps from one actual JVM; original full24/32 and existingADMIN','expected':'SS343 normal existingADMIN exit20 within30s; same source/byte/hashes/window/session; original credentials protected, synthetic fixtures retired, all24 unchanged and all scopes/resources closed','actual':'compile/oracle/verify/execute/post/native qualification0; global four100 incomplete','privateNativeManifestSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frozenHostManifestSha256':m['frozenHostManifestSha256'],'moduleCounters':m['moduleCounters'],'coverage100':m['coverage100'],'formalAccepted':False,'rawExported':False,'relatedBug':['BUG-1000','BUG-1001','BUG-1002'],'relatedYkt':['YKT-769','YKT-770','YKT-771'],'previousFailuresPreserved':['978-v1 bad two-run row fixture actual1','986 verify first missing stage-v1 host preflight1; no guest replay','989-v3 actual post0 but wrong result.run, trace unqualified','initial TDD fixture/label multiplicity failures excluded'],'proofHashes':{n:hashlib.sha256((W/n).read_bytes()).hexdigest()for n in ('pg978-bootstrap-before-v2.safe.json','pg983-frozen-v3.safe.json','pg983-stage-v3.safe.json','pg983-verify-v3.safe.json','pg983-execute-v3.safe.json','pg989-bootstrap-post-v4.safe.json','pg988-bootstrap-fixtures-v1/manifest.safe.json')}}
    changes={};p=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG978-992-current-bootstrap-native-v1/manifest.json';assert not p.exists();changes[p]=(None,json.dumps(public,ensure_ascii=False,indent=2)+'\n')
    p=T/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';old=p.read_text();assert 'current40efBootstrapNativeObservation'not in old
    new=old.replace('  "schemaVersion": 2,','  "current40efBootstrapNativeObservation": '+json.dumps(proof,ensure_ascii=False,separators=(',',':'))+',\n  "schemaVersion": 2,',1);json.loads(new);changes[p]=(old,new)
    print('*** Begin Patch')
    for p,(old,new)in changes.items():
        if old is None:
            print('*** Add File: '+str(p))
            for line in new.splitlines():print('+'+line)
        else:
            print('*** Update File: '+str(p))
            for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]:print('@@'if line.startswith('@@')else line)
    print('*** End Patch')
if __name__=='__main__':main()
