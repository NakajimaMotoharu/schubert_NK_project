"""Classify exactly six intentional negative-fixture diagnostics, without claiming the unselected Root Tests ran."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37166-service9-reused-compile-static-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and p['expectedTests']==9 and not p['processingErrors'] and len(p['rawFindings'])==6
rows=[]
for x in p['rawFindings']:
 path=x['path'];assert sha(r/path)==p['testSourceHashes'][path];text=(r/path).read_text();anchor=text.splitlines()[int(x['beginline'])-1].strip()
 if x['rule']=='ReturnEmptyCollectionRatherThanNull':
  assert ('nullStatus' in anchor or 'nullCommand' in anchor or 'nullSockets' in anchor or 'selected[0].equals("<NULL>")' in anchor)
  reason='Explicit missing byte-array/socket-set negative input, not a successful empty collection. READY428004 requires NPE propagation for missing provider values, never NPE catch/normal success. Root shared source rootctx010 null Unit-deadline vector likewise declares negative input; that Root Test is unselected and no dynamic PASS is claimed. Empty instead of null would remove the independently required missing-value boundary.'
 elif x['rule']=='EqualsNull':
  assert anchor=='assertFalse(first.equals(null));'
  reason='READYVALUE001 directly tests generated immutable Response.equals(Object) with null and literal expected false. Replacing it with first==null would stop exercising the public value method; this is a negative method argument, not a production variable null-check.'
 else:
  assert x['rule']=='DoNotUseThreads' and anchor=='if (bad == INTERRUPTED_WAIT_FIXTURE) assertTrue(Thread.interrupted());'
  reason='Original unselected Root fixture inspects-and-clears the current test-thread interrupt as its required postcondition; it starts no application/managed thread. PMD rule explicitly assumes a J2EE managed container. Source applicability only; neither this Root Test nor the interrupt action is run by the selected9.'
 rows.append(dict(raw=x,sourceSha256=sha(r/path),sourceAnchor=anchor,decision='NOT_APPLICABLE',reason=reason))
for name in ['MorningServiceReadiness.java','RootStartupContext.java']:
 path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/'+name
 assert not any(x['raw']['path']==path for x in ld(b/'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json'))
 assert sha(r/path)==p['mainInputHashes'][path]
mainstatic=ld(r/p['mainSpotBugsCurrentProof']['path']);assert mainstatic['actualExit']==0 and mainstatic['sourceCore']==p['sourceCore']
impact=ld(b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json');assert impact['actualExit']==0 and impact['sourceClosureCount']==17 and all(sha(r/n)==h for n,h in impact['inputHashes'].items())
out=b/'evidence/PG37168-service9-static-admission-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),testSourceStaticScope=2,raw=6,classified=rows,applicable=0,unclassified=0,allChangedTestCallerCompile=ref(b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json'),callerWholeTestsSelected=0,mainSpotbugs=p['mainSpotBugsCurrentProof'],currentMainPmdProof=ref(b/'evidence/PG37092-f03-971-independent-reconcile-v2/manifest.json'),productTestsExecuted=0,sourceRuleSuppressionExclusionChanges=0,wholeRootTestQualityOrRuntimeAccepted=False,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=6,applicable=0,unclassified=0,impactCompile17=True,selectedExpected=9,productTests=0)))
