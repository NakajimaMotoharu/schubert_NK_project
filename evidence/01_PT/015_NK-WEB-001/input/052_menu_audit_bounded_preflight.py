"""Independent fixed fifteen-source/static/SDK preflight; no target invocation or original fixture extraction."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re
import zipfile

R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379'
C=B/'input/050_menu_audit_bounded_scope.json';cfg=json.loads(C.read_bytes())
O=R/cfg['preflightManifest'];assert not O.parent.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes())
pre=load(RUNS/cfg['compileSlot']/'manifest.json');sta=load(RUNS/cfg['staticSlot']/'manifest.json');assert pre['actualExit']==0 and pre['inputHashes']==sta['inputHashes']
for name,pin in pre['inputHashes'].items():assert sha(R/name)==pin
menu=R/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/MenuAuditContractTest.java';text=menu.read_bytes();before=(R/cfg['before']).read_bytes()
old=b'      try (var workers = Executors.newFixedThreadPool(1)) {\n        workers.submit(WebRequestTrace::markMenuViewed).get();\n      }'
new=b'      var workers = Executors.newFixedThreadPool(1);\n      try {\n        workers.submit(WebRequestTrace::markMenuViewed).get(10, TimeUnit.SECONDS);\n      } finally {\n        workers.shutdownNow();\n        assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n      }'
imp=b'import java.util.concurrent.TimeUnit;\n'

def valid(value):
    return value.count(new)==1 and value.count(imp)==1 and value.replace(new,old,1).replace(imp,b'',1)==before

assert valid(text)
negative_vectors=[text.replace(b'.get(10, TimeUnit.SECONDS)',b'.get(90, TimeUnit.SECONDS)'),text.replace(b'workers.shutdownNow();',b''),text.replace(b'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));',b''),text.replace(b'.get(10, TimeUnit.SECONDS)',b'.get(10, TimeUnit.MILLISECONDS)'),text.replace(b'assertFalse(first.menuViewCandidate());',b'assertTrue(first.menuViewCandidate());',1),text.replace(b'newFixedThreadPool(1)',b'newFixedThreadPool(2)')]
assert all(v!=text and not valid(v) for v in negative_vectors)
expected=set()
for name,cls in cfg['testClasses'].items():
    s=(R/name).read_text();methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',s);expected.update((cls,m) for m in methods)
assert len(expected)==15
assert not sta['reports']['checkstyle']['items'] and not sta['reports']['checkstyle']['processingErrors'] and not sta['reports']['pmd']['processingErrors']
assert sta['stages']['checkstyle']['actualExit']==0 and sta['stages']['pmd']['actualExit']==4
items=sta['reports']['pmd']['items'];expected_findings={('MenuAuditContractTest','UseProperClassLoader',107),('MenuAuditContractTest','CloseResource',145),('MenuAuditContractTest','DoNotUseThreads',145),('MenuAuditContractTest','DoNotUseThreads',147),('MenuAuditContractTest','DoNotUseThreads',149),('MenuAuditContractTest','DoNotUseThreads',150),('WebRequestTraceTest','DoNotUseThreads',247),('WebRequestTraceTest','DoNotUseThreads',248),('WebRequestTraceTest','DoNotUseThreads',252),('WebRequestTraceTest','DoNotUseThreads',272),('WebRequestTraceTest','DoNotUseThreads',277)}
assert len(items)==11 and {(r['class'],r['rule'],int(r['beginline'])) for r in items}==expected_findings
classifications=[]
for row in items:
    if row['rule']=='CloseResource':reason='Own executor never escapes: finally shutdownNow then bounded awaitTermination(10SECONDS) asserted; no AutoCloseable.close call because that can wait without a local deadline. New whole test must prove normal termination.'
    elif row['rule']=='UseProperClassLoader':reason='Own Model proxy uses exact declaring Model.class loader for interface identity; memory Spring unit is not a J2EE container. Callback always throws the same synthetic failure before marker.'
    else:reason='JUnit-only owned thread/executor and finite Future waits; no server component. Changed Menu worker uses explicit finite shutdown confirmation, original trace workers finish through existing 5-second results and owned TWR. Unit OS completion and independent no contamination assertions required.'
    classifications.append(dict(finding=row,applicableViolation=False,reason=reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for name in cfg['mainPaths']:assert sha(R/name)==nm['begin']['inputHashes'][name]
for module in cfg['modules']:assert sha(Path(nm['jars'][module]['path']))==nm['jars'][module]['sha256']
for name,h in pre['dependencies'].items():assert sha(Path(name))==h
sdk=[]
for name,h in cfg['sdkDependencies'].items():
    p=Path(name);assert sha(p)==h
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist());assert not names.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
        mf=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in names else ''
        assert not re.search(r'^Class-Path:',mf,re.M)
    sdk.append(dict(path=name,sha256=h,jdbcDriverDescriptor=False,compilerPluginDescriptor=False,manifestClasspath=False))
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(index_path)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(index_path)
expected_physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert expected_physical==cfg['currentMainPhysical'] and set(expected_physical)==set(cfg['targetPhysical']) and len(expected_physical)==4
prior_path=R/cfg['previousWholeManifest'];prior=load(prior_path);assert sha(prior_path)=='d8be18461ee3436e92752f09ce00fe3e9f70ee5c2edcb51c3fa32aa7060c5adc';ep=prior_path.parent/'execinfo.stdout';assert sha(ep)==prior['files']['execinfo.stdout']
old_probes={n:(i,int(h)) for i,h,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ep.read_text(),re.M)}
test_prefixes=[name.replace('.','/') for name in cfg['testClasses'].values()];positive={n:i for n,(i,h) in old_probes.items() if n.startswith('dev/codex/schubert/nk/') and h>0 and not any(n==p or n.startswith(p+'$') for p in test_prefixes)}
assert len(positive)==20 and all(n in index and index[n]['crc64']==i for n,i in positive.items())
assert prior['physicalHashes']==expected_physical
O.parent.mkdir()
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=pre['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),originalCurrentMainCodeByteSetComplete=True,physical=expected_physical,expectedTests=15,changedFutureSites=1,finiteOwnerShutdown=True,allOriginalTestOtherBytesPreserved=True,sourceInverseNegativeChecks=6,staticClassifications=classifications,pmdRawFindings=11,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,sdkReview=sdk,priorPublicExecinfoMetadataRead=True,historicalPositiveMainCrcSame=20,originalExecBinaryOrPrivateRawRead=False,normalPositiveMainIndex={'path':str(index_path.relative_to(R)),'sha256':sha(index_path)},currentProductionMain=nm['source'],originalWholeTestClassSelection=True,noNewFixtureOrMethodExtraction=True,heldFourRuntimeOperationsAuthorized=False,actualBackendOperationsAuthorized=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
O.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,originalMethods=15,targetPhysical=4,pmdRaw=11,applicable=0,originalPositiveMainSame=20,manifestSha256=sha(O))))
