from pathlib import Path
import json,hashlib,datetime,subprocess
r=Path.cwd(); root=r/'evidence/01_PT/005_NK-MSG-001'; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
paths=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'+n+'.java' for n in ['messaging/ArtemisReplyConsumers','bootstrap/WebNativeRuntime','bootstrap/WebRuntimeStop','bootstrap/WebHttpAdmission','bootstrap/WebHttpAdmissionValve']]+['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiLogPathApplicationRuntime.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStopTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumersTest.java']
normalp=r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json'; normal=json.loads(normalp.read_text()); pins={}
for n in paths:
 pins[n]=sha(r/n);assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest()==pins[n]
 if '/src/main/' in n:assert pins[n]==normal['begin']['inputHashes'][n]
review=root/'029_YKT2152_Web応答・外側owner静的横展開.md';pins[str(review.relative_to(r))]=sha(review)
text=(r/paths[0]).read_text();assert text.count('context.close();')==2 and 'stopping = true' in text
outer=(r/paths[1]).read_text();assert outer.index('admission.refuse()')<outer.index('admission.drain(')<outer.index('replies.close()')
api=(r/paths[5]).read_text();assert 'messaging.close();' in api
out=root/'evidence/PG21998-ykt2152-web-outer-static-v1';assert not out.exists();out.mkdir()
m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=normal['source'],normalManifestSha256=sha(normalp),inputHashes=pins,reviewTargets=['ArtemisReplyConsumers: one context, no untouched sibling fanout','WebNativeRuntime: HTTP admission refusal followed by existing HTTP/worker/reply order','ApiLogPathApplicationRuntime: delegates to fixed messaging owner'],existingTestDesignOnly={'WebRuntimeStopTest':'whole five bodies','ArtemisReplyConsumersTest':'closeIsIdempotentAndPreservesStartupAndCloseFailures body only'},newFinding='BUG-2409/YKT-2154 signed clock deadline comparison; separate cause, not runtime reproduction',productTestsExecuted=0,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,coverage=None,bugsRemainOpen=['BUG-2407','YKT-2152','BUG-2409','YKT-2154'],ptExecutionExempt=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifestSha256=sha(out/'manifest.json'))))
