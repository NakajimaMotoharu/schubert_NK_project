"""Seal exact original4 continuity/static/Main metadata; no test execution."""
from pathlib import Path
import ast,datetime as dt,hashlib,json,re,subprocess
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; E=B/'evidence'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before=load(E/'PG26012-saved-target-before-v1/manifest.json');r=before['sources'][0]
old=subprocess.check_output(['git','show',r['gitBlobObjectIdSHA1']],text=True)
assert hashlib.sha256(old.encode()).hexdigest()==r['sha256']
p=R/r['path'];cur=p.read_text();flat=lambda t:re.sub(r'\s+','',t)
inverse=flat(cur);a='varpool=Executors.newFixedThreadPool(10);try{';b='try(varpool=Executors.newFixedThreadPool(10)){'
assert inverse.count(a)==1;inverse=inverse.replace(a,b)
tail='}finally{pool.shutdownNow();org.junit.jupiter.api.Assertions.assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}'
assert inverse.count(tail)==1;inverse=inverse.replace(tail,'}')
assert inverse==flat(old) and re.findall(r'"(?:\\.|[^"\\])*"',cur)==re.findall(r'"(?:\\.|[^"\\])*"',old)
assert cur.count('@Test')==4 and cur.count('future.get(20, TimeUnit.SECONDS)')==1
prepPath=E/'PG26014-saved-target-configured-prepare-v1/manifest.json';prep=load(prepPath)
assert prep['actualExit']==0 and prep['testSourceHashes']=={r['path']:sha(p)}
assert '--skip-reflowing-long-strings' in prep['stages']['format']['command']
assert prep['reports']['checkstyle']['rawFindings']==0
findings=prep['reports']['pmd']['findings'];assert len(findings)==5
for f in findings:
 assert f['class']=='SavedRequestTargetTest' and f['method']=='web008ConcurrentTargetsRemainIndependent' and f['rule'] in ['DoNotUseThreads','CloseResource']
P=E/'PG26016-saved-target-current-console-preflight-v1';assert not (P/'manifest.json').exists()
pf=load(P/'draft.json');entry=R/pf['entrypointPath'];ast.parse(entry.read_text())
assert pf['entrypointSha256']==sha(entry) and 'PG26018-SAVED-TARGET-ORIGINAL-WHOLE4' in entry.read_text()
assert 'pg26018-saved-target-original-whole4-v1' in entry.read_text() and 'PG26018-saved-target-original-whole4-v1' in entry.read_text()
assert pf['expectedTests']==4 and pf['selected']==['dev.codex.schubert.nk.web.security.SavedRequestTargetTest']
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for key in ['metadataInventory','physicalIndex']:
 ref=pf[key];assert sha(R/ref['path'])==ref['sha256']
meta=load(R/pf['metadataInventory']['path']);target=[v for v in meta if v['sourcePath']==before['main']['path']]
assert len(target)==1 and target[0]['classSha256']==next(iter(pf['targetClassHashes'].values())) and sha(R/before['main']['path'])==before['main']['sha256']
app=E/'PG26016-saved-target-source-static-v1';assert not app.exists();app.mkdir()
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),originalFourAssertionsUnchanged=True,originalSha256=r['sha256'],currentSha256=sha(p),testPath=r['path'],beforeManifestSha256=sha(E/'PG26012-saved-target-before-v1/manifest.json'),finiteOwnerSitesCorrected=1,ownerTimeoutSeconds=10,existingFutureGet20SitesRetained=1,rawFindings=5,applicableViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,classifications=[dict(f,applicable=False,basis='Test-owned pool10 only; shutdownNow and asserted await10 in finally; all submitted Future get20 retained. No external resources.') for f in findings],staticManifest=dict(path=str(prepPath.relative_to(R)),sha256=sha(prepPath)),productTestsExecuted=0,newAcceptance=0)
write(app/'manifest.json',v);pf.update(atJST=v['atJST'],sourceContinuityAndStatic=dict(path=str((app/'manifest.json').relative_to(R)),sha256=sha(app/'manifest.json')),configuredSelectedFormat=dict(path=str(prepPath.relative_to(R)),sha256=sha(prepPath)),preflightActualWholeCases=4,preflightActualMainSources=1,fullOriginalBodiesExactlyRestored=True)
write(P/'manifest.json',pf);print(json.dumps(dict(actualExit=0,originalCases=4,ownerSites=1,existingGet20=1,rawPmd=5,applicable=0,manifestSha256=sha(P/'manifest.json'))))
