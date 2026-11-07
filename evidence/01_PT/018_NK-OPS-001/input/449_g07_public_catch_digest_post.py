"""Independent zero-credit boundary proof; no target execution, private raw or scanner."""
from pathlib import Path
from collections import Counter
import json,hashlib,ast,datetime,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001/evidence';S=B/'PG23518-g07-public-catch-digest-v1';O=B/'PG23520-g07-public-catch-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();key=lambda x:tuple(x[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert not O.exists();m=load(S/'manifest.json');assert sha(S/'manifest.json')=='4451a939355e277d918108f3ceaaa95facc55d56eb88e0044f3316da54fde4a8';assert m['actualExit']==0 and m['newFalsePositives']==0 and m['remainingUnclassified']==4482 and m['retainedRows']==73;assert sha(S/'updates.json')==m['updatesSha256'] and load(S/'updates.json')==[];retained=load(S/'retained.json');assert sha(S/'retained.json')==m['retainedSha256']
origin=B/'provisional/PG9888-g07-capture-shape-v1/residual-metadata-shapes.json';assert sha(origin)==m['originalMetadataSha256'];rows=load(origin);assert len(rows)==4493;original=Counter(map(key,rows));done=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];done.extend(load(p))
old=Counter(map(key,done));assert len(done)==11 and sum((original-old).values())==4482
p=R/m['input']['path'];assert sha(p)==m['input']['sha256'];sites=load(p);text=p.read_text();assert len(sites)==113;selected=[x for x in rows if x['path']==m['input']['path'] and not old[key(x)]];assert len(selected)==73 and Counter(map(key,selected))==Counter(map(key,retained));assert all(x['status']=='SOURCE_NOT_IN_EXACT_ALLOWED_READ_SET' for x in retained)
expected={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OwnedOutboxDispatcher.java','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogReplayWorker.java'};assert set(m['allowedSources'])==set(m['sourcePins'])==expected
# Independently associate pretty JSON property lines by top-level object number,
# not the producer's raw_decode absolute-span calculation.
idx=-1;lineobjects={}
for line_no,line in enumerate(text.splitlines(),1):
 if line=='  {':idx+=1
 if line.strip().startswith('"bodyTokenSha256":'):
  assert idx>=0;lineobjects[line_no]=sites[idx]
assert idx+1==113 and len(lineobjects)==113
for finding in selected:
 assert finding['startLine']==finding['endLine'] and finding['startLine'] in lineobjects
 obj=lineobjects[finding['startLine']];assert obj['sourcePath'] not in expected and finding['inputSha256']==sha(p)
for n,h in m['sourcePins'].items():
 assert n in expected;src=R/n;assert not src.is_symlink() and src.resolve()==src and sha(src)==h
producer=R/m['tool']['path'];assert sha(producer)==m['tool']['sha256'];t=producer.read_text();tree=ast.parse(t);allow=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='ALLOW' for n in x.targets));assert allow==expected
assert 'for n in sorted(ALLOW):\n assert source_allowed(n);src=R/n;' in t and 'if not source_allowed(n):retained.append(' in t
# Path-only regression facts: candidates never touch File APIs before explicit membership.
def permit(n):return n in expected
negative_paths=['tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootFailedStartRecoveryTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootFailedStartPairRecoveryTest.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AdminCommandAuthenticator.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionService.java','../private/raw.log','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/file/RootOwner.java','unknown.json'];assert all(not permit(n) for n in negative_paths) and all(permit(n) for n in expected)
def contract(v):
 assert v['newFalsePositives']==0 and v['remainingUnclassified']==4482 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and set(v['sourcePins'])==expected and all(v[k] is False for k in ['scannerExecuted','targetsExecuted','privateRawRead','capturedValuesWritten','captureValueHashesWritten','wholeG07Accepted','whole451Accepted']) and v['productTestsExecuted']==v['actualBackendActions']==v['newAcceptance']==0
contract(m);badcases=[('newFalsePositives',1),('remainingUnclassified',4481),('actualSecretCount',0),('binaryOrContainerLimited',0),('sourcePins',{}),('privateRawRead',True),('productTestsExecuted',1),('wholeG07Accepted',True)]
for k,v in badcases:
 wrong=copy.deepcopy(m);wrong[k]=v
 try:contract(wrong)
 except AssertionError:pass
 else:raise AssertionError('bad boundary claim accepted')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceManifest=dict(path=str((S/'manifest.json').relative_to(R)),sha256=sha(S/'manifest.json')),checkedOriginalRows=4493,previousUpdates=11,candidateRows=73,safeSourceReadSet=sorted(expected),safeCurrentSourcesPinned=2,pendingRowsWithinAllowedSources=0,remainingUnclassified=4482,newFalsePositives=0,actualSecretCount=None,binaryOrContainerLimited=22,scopeGuardNegativeChecks=len(negative_paths),claimMetadataNegativeChecks=len(badcases),originalDraftSpanFailure='PG23526',guardRemedy=dict(bug='BUG-2490',horizontal='YKT-2228',priorOffScopeChecksumsExcludedFromClassification=True,exactWhitelistBeforeSourceIO=True),productTestsExecuted=0,scannerExecuted=False,privateRawRead=False,targetsExecuted=False,capturedValuesWritten=False,captureValueHashesWritten=False,newAcceptance=0,formalUpdated=False,wholeG07Accepted=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,classified=0,pendingInAllowed=0,remaining=4482,pathNegatives=10,metadataNegatives=8,manifestSha256=sha(O/'manifest.json'))))
