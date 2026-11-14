"""Exact source/site applicability for all sixty raw rules; no global filter or source suppression."""
from pathlib import Path
import collections,datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';w=r.parent/'pgpt-runs/PG379/pg30726-haruka-common91-v3';sp=b/'evidence/PG30728-haruka-common91-full-static-raw-v3/manifest.json';s=json.loads(sp.read_text());cfg=json.loads((w/'payload-config.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert s['sourceCommit']==cfg['sourceCommit']=='f9f9d28f23833257be991d142e105ec4533f7be8'
assert s['compileStatic']['actualExit']==0 and s['compileStatic']['ownedProcessGroupAbsent'] is True
assert not s['processingErrors'] and s['checkstyleErrors']==0 and all(v==0 for v in s['spotbugs'].values())
counts=collections.Counter(x['rule'] for x in s['rawFindings']);assert counts==dict(UseConcurrentHashMap=24,CloseResource=6,DoNotUseThreads=29,UseProperClassLoader=1)
prefix='/home/mini/schubert-nk-pgpt/runs/pg30726-common91-v3/payload/source/'
# Each binding was read as a whole method: maps are fresh invocation/fixture state, never shared storage.
bindings={
 'ArtifactComparator.java':{('compare','currentByCase'),('compare','nkByCase'),('compare','rules'),('artifactFiles','files')},
 'CorrelatedLogEvidenceValidator.java':{('expectations','events'),('compareSide','addedEvents'),('rows','rows')},
 'GateCli.java':{('verifySource','actual'),('preflight','result'),('compareCurrent','result'),('report','result'),('promoteCurrent','manifest'),('prefixed','result'),('fileHashes','result')},
 'GateContractValidator.java':{('gateMetrics','metrics')},
 'ArtifactComparatorTest.java':{('fixture','currentArtifacts'),('fixture','nkArtifacts')},
 'GateCliTest.java':{('mainRejectsMissingUnknownAndIncompleteCommands','missingProjectRoot'),('verifySourceAcceptsIndependentInventoryAndRejectsDriftAndSymlink','expected'),('preflightValidatesFilesPermissionsStorageNetworkAndPorts','invalidProperties'),('preflightRejectsParentlessLogPathWithoutNpe','properties'),('assertPortFailure','properties'),('preflightFixture','properties'),('withProperties','previous')},
}
workers={'GateCliTest.java','CorrelatedLogEvidenceValidatorTest.java','BaselineNumericMetadataTest.java','GateMetricsCountTest.java','GateDefinitionDocumentsTest.java','GateEvidenceDocumentsTest.java'}
seen_maps=set();rows=[]
for raw in s['rawFindings']:
 assert raw['path'].startswith(prefix)
 name=raw['path'][len(prefix):];p=r/name;text=p.read_text();line=int(raw['beginline']);anchor=text.splitlines()[line-1].strip()
 assert cfg['payloadHashes']['source/'+name]==sha(p)
 rule=raw['rule'];base=p.name
 if rule=='UseConcurrentHashMap':
  binding=(raw['method'],raw['variable']);assert binding in bindings[base]
  key=(base,*binding);assert key not in seen_maps;seen_maps.add(key)
  assert re.search(r'new (?:java\.util\.)?(?:TreeMap|LinkedHashMap|HashMap)<>',anchor)
  reason='Exact method '+raw['method']+' allocates '+raw['variable']+' freshly per invocation/fixture; synchronous use, no static/instance publication or concurrent sharing. Sorted/ordered maps preserve canonical metadata and property restoration may retain null. The conditional concurrent-access rule does not apply to this local map.'
  if base=='GateContractValidator.java':
   assert 'return Map.copyOf(metrics);' in text
   reason+=' gateMetrics publishes only Map.copyOf(metrics), an immutable snapshot.'
  if base=='GateCliTest.java':reason+=' JUnit cases run sequentially by default with no enabling property; owned worker cases never mutate system properties.'
 elif rule in ('CloseResource','DoNotUseThreads'):
  assert base in workers
  assert 'finally {' in text and '.shutdownNow();' in text
  assert re.search(r'assertTrue\s*\(\s*(?:workers|executor)\.awaitTermination\(10, TimeUnit\.SECONDS\)',text)
  assert re.search(r'\.get\(5, TimeUnit\.SECONDS\)',text)
  assert not re.search(r'\b(?:good|bad|valid|invalid|first|second)\.get\(\)',text)
  if rule=='CloseResource':
   reason='This exact JUnit-owned executor is acquired before try; every exit reaches finally shutdownNow and checked awaitTermination10. Each Future joins5, Gate serialization helper also has await5 and finally releases its latch. No returned/shared resource; implicit ExecutorService.close would lack the explicit finite postcondition.'
  else:
   reason='This exact site is standalone pure-data/fixture JUnit, not a J2EE managed webapp. Its locally owned executor is bounded by Future5 and finallyshutdownNow/await10 with failing postcondition. No application/container threads, DB/native/process/service/Root operation is introduced.'
 else:
  assert rule=='UseProperClassLoader' and base=='GateContractTest.java' and raw['method']=='resource'
  assert anchor=='try (InputStream input = GateContractTest.class.getClassLoader().getResourceAsStream(name)) {'
  reason='This private standalone JUnit helper loads only the four explicitly named pinned public contract resources from its defining test classloader, with a missing-resource check and TWR. No J2EE/container or caller-supplied context loader participates; changing to an ambient context loader would weaken fixture provenance.'
 rows.append(dict(path=name,sha256=sha(p),sourceLine=line,sourceAnchor=anchor,method=raw.get('method'),variable=raw.get('variable'),rule=rule,message=raw['message'],disposition='NOT_APPLICABLE',reason=reason))
assert len(seen_maps)==24 and len(rows)==60
ad=dict(schema='PGPT_HARUKA_COMMON91_STATIC_ADMISSION_V1',sourceCommit=s['sourceCommit'],prepareSha256=sha(sp),rawCount=60,applicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,allSourcePinsExact=True,sourceAnchors=rows,sourceSuppressions=[],qualityRuleChanges=[],coverageExclusions=[],expectedTests=91,oldExecCombined=False,formalAccepted=False)
p=i/'2571_common91_exact_static_admission.json';assert not p.exists();p.write_text(json.dumps(ad,ensure_ascii=False,indent=2)+'\n')
e=b/'evidence/PG30724-common91-full-static-independent-applicability-v1';assert not e.exists();e.mkdir();m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=s['sourceCommit'],productionCoreMain=cfg['productionCoreMain'],static=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),admission=dict(path=str(p.relative_to(r)),sha256=sha(p)),raw60PerSiteReviewed=True,applicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,oldV2Applicable16RetestedZero=True,wholeNinetyOneStillNotRun=True,newProductTestsExecuted=0,allSpecificHoldsRetained=True,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=60,exactSourceClassified=60,applicable=0,unclassified=0,unitNotRun=True)))
