"""A4-01 before/fix/configured static/preflight; full original four, no network or held dependency."""
from pathlib import Path
import datetime as dt,hashlib,json,re,subprocess,sys
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; E=B/'evidence'
sys.path[:0]=[str(R/'tools/quality')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/SavedRequestTargetTest.java'
main=test.replace('/test/','/main/').replace('SavedRequestTargetTest.java','SavedRequestTarget.java')
prior=load(E/'PG26004-quota-preservation-restart-v1/next-restart.json')
for p,h in prior['nextCandidate']['sourceHashes'].items():assert sha(R/p)==h
before=E/'PG26012-saved-target-before-v1';assert not before.exists();before.mkdir()
blob=subprocess.check_output(['git','rev-parse','HEAD:'+test],text=True).strip()
old=(R/test).read_text();assert hashlib.sha256(subprocess.check_output(['git','show',blob])).hexdigest()==sha(R/test)
write(before/'manifest.json',dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),bug='BUG-2623',sourceHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),sources=[dict(path=test,sha256=sha(R/test),gitBlobObjectIdSHA1=blob)],main=dict(path=main,sha256=sha(R/main)),sourceObservedOwnerSites=1,existingGet20Sites=1,testsNotStarted=True,expectation='Bound owned executor termination; preserve all four original independent URL expectations.'))
opening='    try (var pool = Executors.newFixedThreadPool(10)) {'
assert old.count(opening)==1
new=old.replace(opening,'    var pool = Executors.newFixedThreadPool(10);\n    try {')
tail='      for (var future : futures) future.get(20, TimeUnit.SECONDS);\n    }'
assert new.count(tail)==1
new=new.replace(tail,tail[:-1]+'} finally {\n      pool.shutdownNow();\n      org.junit.jupiter.api.Assertions.assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));\n    }')
(R/test).write_text(new)
# Reuse the current fixed formatter/static profile, not its old source or counters.
base=(B/'input/1061_web_security_audit_configured_prepare.py').read_text()
for a,b in [('pg25954-security-audit','pg26014-saved-target'),('PG25954-security-audit','PG26014-saved-target'),('PG25952-security-audit-owner-before-v1','PG26012-saved-target-before-v1'),("['WebSecurityAuditTest']","['SavedRequestTargetTest']"),("==[6]","==[4]")]:
 assert a in base,a;base=base.replace(a,b)
start=base.index('vendor=');end=base.index(';aux=',start)
base=base[:start]+'vendor=[]'+base[end:]
line="assert sum(p.read_text().count('.invokeAll(jobs, 10, TimeUnit.SECONDS)') for p in tests)==1 and "
assert line in base;base=base.replace(line,'assert ')
prepentry=B/'input/1073_saved_target_configured_static.py';assert not prepentry.exists();prepentry.write_text(base)
# Bind Main/POM bytes to the reusable normal compile, with the target's actual metadata.
oldpf=load(E/'PG25716-web-csrf-token-current-console-preflight-v1/manifest.json')
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
assert sha(normal)==oldpf['normalManifestSha256'];nm=load(normal)
assert type(nm['actualExit']) is int and nm['actualExit']==0 and nm['testsExecuted'] is False
meta=load(R/oldpf['metadataInventory']['path']);targets=[r for r in meta if r['sourcePath']==main]
assert len(targets)==1 and targets[0]['costOwner']=='WBS-P015-02'
for path in [main,'pom.xml','src/schubert-nk-web/pom.xml']:assert sha(R/path)==nm['begin']['inputHashes'][path]
runner=(R/'tools/quality/pg25718_web_csrf_value_original_four_pt.py').read_text()
for a,b in [('web-csrf-token','saved-target'),('25718','26018'),('25716','26016'),('WebCsrfTokenTest','SavedRequestTargetTest'),('WEB-CSRF-TOKEN','SAVED-TARGET')]:
 assert a in runner,a;runner=runner.replace(a,b)
runner=runner.replace('Original CSRF values whole4, fixed public fixture/ephemeral in-memory PRNG only, no deployed secrets.','Original SavedRequestTarget whole4; pure JDK URI parsing, bounded own pool; no network or credentials.')
entry=R/'tools/quality/pg26018_saved_target_original_four_pt.py';assert not entry.exists();entry.write_text(runner)
designs={}
for p,ref in oldpf['approvedDesigns'].items():
 if Path(p).name.startswith(('314_','352_','226_')):
  data=subprocess.check_output(['git','show','origin/main:'+p]);designs[p]=dict(approvedMain=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),sha256=hashlib.sha256(data).hexdigest())
pf=dict(oldpf);pf.update(entrypointPath=str(entry.relative_to(R)),entrypointSha256=sha(entry),inputHashes={p:sha(R/p) for p in [test,main,'pom.xml','src/schubert-nk-web/pom.xml']},testPaths=[test],targetClassHashes={r['physicalKey'].split(':',1)[1]:r['classSha256'] for r in targets},targetClassNames=[r['physicalKey'].split(':',1)[1] for r in targets],allowedObservedMain=[r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in targets],selected=['dev.codex.schubert.nk.web.security.SavedRequestTargetTest'],expectedCaseCounts={'dev.codex.schubert.nk.web.security.SavedRequestTargetTest':4},approvedDesigns=designs,ephemeralGeneratedValuesExported=False)
O=E/'PG26016-saved-target-current-console-preflight-v1';assert not O.exists();O.mkdir();write(O/'draft.json',pf)
print(json.dumps(dict(actualExit=0,beforeSha256=sha(before/'manifest.json'),productTestsExecuted=0,next='lint1073 then configured static; seal preflight only after result0 and exact inverse')))
