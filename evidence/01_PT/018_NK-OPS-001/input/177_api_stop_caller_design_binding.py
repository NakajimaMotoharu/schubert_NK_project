"""Whole caller Test source/expectation binding only; never compile or invoke its helpers."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();test='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetimeTest.java';text=(r/test).read_text();methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);assert len(methods)==len(set(methods))==14
normalp=r.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=json.loads(normalp.read_text());assert sha(normalp)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and normal['actualExit']==0
mainroot='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/';pins={test:sha(r/test)}
for n in [mainroot+'ApiProcessLifetime.java',mainroot+'ApiStopBudget.java']:
 pins[n]=sha(r/n);assert pins[n]==normal['begin']['inputHashes'][n]
review=r/'evidence/01_PT/018_NK-OPS-001/3637_API停止caller全十四Test_静的設計レビュー.md';ids=['REV-API-CALLER'+str(i).zfill(3) for i in range(1,15)];assert all(review.read_text().count('| '+n+' |')==1 for n in ids)
pins[str(review.relative_to(r))]=sha(review)
for n in pins:assert pins[n]==hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest()
assert 'new ProcessBuilder(command).start()' in text and 'new ProcessBuilder("/usr/bin/kill", "-TERM"' in text and 'assertThrows(TemporaryInfrastructureException.class' in text
for method in methods:assert review.read_text().count(' / '+method+' |')==1
existingRefs=[]
for n in ['evidence/01_PT/018_NK-OPS-001/305_NK-OPS-001_API管理ready・所有寿命単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/1872_APILifetimeBudget_限定製造・単体仕様.md','evidence/01_PT/018_NK-OPS-001/3633_API停止通知一体化_独立PT仕様.md','evidence/01_PT/018_NK-OPS-001/3634_API停止通知一体化_実行結果.md']:
 existingRefs.append(dict(path=n,sha256=sha(r/n)))
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22140-api-stop-caller-fourteen-static-design-v1';assert not out.exists();out.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=normal['source'],inputHashes=pins,wholeExistingTestMethodsReviewedOnly=methods,reviewIds=ids,existingOracleRefs=existingRefs,helperSourceOnly=['event','HookDriver.main'],legacyReady006Subcases={'TERM':'ready006ActualJvmTermWaitsMainOwnerAndNeverSelfExits','HOOK':'ready006HookWaitsOuterOwnerAndRestoresInterrupt'},callerNewPendingIds=['PT-OPS-API-STOP-OWNER'+str(i).zfill(3) for i in range(1,4)],testStatus='NOT_RUN_HOLD',compileAndProductInvocations=0,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,coverage=None,ptExecutionExempt=False,bugsRemainOpen=['BUG-2416','YKT-2161'],whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testBodiesReviewedOnly=14,productTests=0,manifestSha256=sha(out/'manifest.json'))))
