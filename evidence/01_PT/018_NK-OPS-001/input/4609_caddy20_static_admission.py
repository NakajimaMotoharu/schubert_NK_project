"""Nine exact memory fixture diagnostics; full Main NativeIo remains unexecuted/uncovered."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37134-caddy20-prepare-static-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and not p['processingErrors'] and len(p['rawFindings'])==9
rows=[]
for x in p['rawFindings']:
 path=x['path'];assert sha(r/path)==p['testSourceHashes'][path];text=(r/path).read_text();anchor=text.splitlines()[int(x['beginline'])-1].strip()
 if x['rule']=='CloseResource' and 'stream(closes,' in anchor:
  assert anchor in ['var input = stream(closes, null);','var input = stream(closes, failure);'];reason='CADDYSTREAM001/004 deliberately transfer this memory InputStream to closeLoginInput/ResourceScope; source requires owned close exactly once on success and injected IO/Runtime/Error. The independent counters assert1; test-side second close would invalidate ownership. No actual HTTP/FS stream.'
 else:
  assert x['rule'] in ['CloseResource','DoNotUseThreads']
  if x['rule']=='CloseResource':assert anchor=='var executor = Executors.newFixedThreadPool(2);'
  assert all(v in text for v in ['first.get(5, TimeUnit.SECONDS)','second.get(5, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));','@Timeout(30)'])
  reason='CADDYSTREAM006 whole ordinary standalone JUnit: two tasks with separate memory stream ownership, two get5s, finally shutdownNow/asserted await10s, latch10s and whole Test30s/outer JVM120s. Thread interrupt at streamBarrier restores interruption before fixed IO. PMD DoNotUseThreads is a J2EE managed-container restriction; no application thread, actual backend or service owner is created.'
 rows.append(dict(raw=x,sourceSha256=sha(r/path),sourceAnchor=anchor,decision='NOT_APPLICABLE',reason=reason))
root=ld(r/p['mainSpotBugsCurrentProof']['path']);assert sha(r/p['mainSpotBugsCurrentProof']['path'])==p['mainSpotBugsCurrentProof']['sha256'] and root['actualExit']==0 and root['sourceCore']==p['sourceCore']
main='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningCaddyReadiness.java';classified=ld(b/'evidence/PG37092-f03-971-independent-reconcile-v2/all-current-dispositions.json');sites=[x for x in classified if x['path']==main];remaining=ld(b/'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json');assert not any(x['raw']['path']==main for x in remaining);assert sites and all(x['sourceSha256']==sha(r/main) for x in sites)
out=b/'evidence/PG37136-caddy20-static-admission-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),testRaw=9,classified=rows,applicable=0,unclassified=0,currentMainPmdSites=len(sites),currentMainPmdProof=ref(b/'evidence/PG37092-f03-971-independent-reconcile-v2/manifest.json'),currentMainSpotbugs=p['mainSpotBugsCurrentProof'],sourceRuleOrSuppressionChanges=0,productTestsExecuted=0,mainNativeIoActualProof=False,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testRaw=9,mainPmdSites=len(sites),applicable=0,unclassified=0,productTests=0)))
