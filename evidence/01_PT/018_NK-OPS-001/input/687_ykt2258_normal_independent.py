"""Independent explicit case-path review; public source only, without replaying DB/key fixtures."""
from pathlib import Path
import datetime,hashlib,json,re
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG24288-ykt2258-sibling-normal-fixture-v1/manifest.json';O=B/'evidence/PG24290-ykt2258-sibling-normal-independent-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads(P.read_bytes());assert sha(P)=='232413e4b90200928bc7a66a362e4f434cf0c0b7bc0ceee9eb726e657f473040' and m['actualExit']==0
assert len(m['rows'])==2 and m['registeredTargets']==3
expected={'WebLogReplayWorker':dict(method='temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails',failed=2),'RevocationRetryWorker':dict(method='rerun008bTransientFailureRecoveryAndFatalTerminalNeverExposeProvider',failed=1)}
for row in m['rows']:
 name=Path(row['main']).stem;assert name in expected and row['method']==expected[name]['method']
 assert sha(R/row['main'])==row['mainSha256'] and sha(R/row['test'])==row['testSha256']
 text=(R/row['test']).read_text();part=text.split('void '+row['method']+'(',1)[1].split('\n  @Test',1)[0];assert hashlib.sha256(part.encode()).hexdigest()==row['methodReviewedSha256']
 assert len(re.findall(r'@Test\s+void\s+',text))>1 # preserve complete original class, no extraction
 if name=='WebLogReplayWorker':
  assert part.index('if (call == 1)')<part.index('if (call == 2)')<part.index('return EMPTY;')<part.index('completedCycles() >= 1')
  assert 'assertEquals(2, snapshot.failedCycles());' in part and 'assertEquals(EMPTY, snapshot.last());' in part
 else:
  ordinary=part.split('for (boolean nested',1)[0]
  assert ordinary.count('throw new IllegalStateException')==1 and 'if (calls.incrementAndGet() == 1)' in ordinary
  assert 'completedCycles() > 0' in ordinary and 'assertEquals(1, worker.snapshot().failedCycles());' in ordinary
 assert not row['currentRuntimeQualified'] and row['coverage'] is None
 assert len(row['negativeChecks'])==len(row['testRequiredAtoms'])+len(row['mainRequiredAtoms'])
 assert row['normalReturnContractPresent'] and row['currentMainMatchesNormal']
ref=m['newRegressionTestRef'];assert sha(R/ref['path'])==ref['sha256'];o=json.loads((R/ref['path']).read_bytes())
assert (o['actualExit'],o['tests'],o['newUniqueTests'])==(0,7,1) and all(o['coverage'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceOnlySiblingNonApplicable=2,ownedFixedTarget=1,registeredTargetsDispositionComplete=True,limitedYktCauseClosed=True,sourceRuntimeQualificationInferred=False,allSiblingDynamicHoldsPreserved=True,originalTestBodiesRetained=True,newRegressionActualRef=ref,originalReviewManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),individualCases=[dict(className=n,method=v['method'],normalAfterTransientFailures=True,expectedFailureCycles=v['failed']) for n,v in expected.items()],counterOrFormalOrLeafIncrease=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,bugs=['BUG-2524'],ykts=['YKT-2258'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,limitedYktCauseClosed=True,siblingRuntimeStillHold=2,manifestSha256=sha(O/'manifest.json'))))
