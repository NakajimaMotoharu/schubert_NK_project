"""Fresh same-group Root Main10, original boundary4 and new value4; no backend capability."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG35023-batch-data8-test-recompile-v1/manifest.json';sp=b/'evidence/PG35025-batch-data8-static-v2/manifest.json';cp=b/'evidence/PG35028-batch-data8-source-v2/manifest.json';m=ld(pp);s=ld(sp);src=ld(cp);o=b/'evidence/PG35026-batch-data8-preflight-v1';assert not o.exists()
assert m['actualExit']==s['actualExit']==src['actualExit']==0 and m['expectedTests']==8 and len(m['apiMainSources'])==10 and len(m['apiTestSources'])==3 and src['originalBoundary4ByteExact'] and src['fixedLiteralInverseByteExact'];assert m['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(s,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert s['processingErrors']==[] and s['rawFindings']==[] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','errors','missing'])
w=r.parent/'pgpt-runs/PG379/pg35022-batch-data8-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(w/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==186 and len(m['mainClassHashes'])==10 and {v.replace('.','/')+'.class' for v in s['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(n))==h for n,h in m['dependencies'].items())
rootp=r/m['sameGroupOriginalRootCompile']['path'];root=ld(rootp);assert sha(rootp)==m['sameGroupOriginalRootCompile']['sha256'] and all(root['inputHashes'][n]==m['inputHashes'][n] for n in m['apiMainSources']) and root['mainClassHashes']==m['mainClassHashes'];assert m['MainBinaryReusedSinceFirstPrepareInSameGroup'] and m['MainSourceAndBinaryUnchangedAfterFixtureStyleFix']
providers={}
for n in m['dependencies']:
 with zipfile.ZipFile(n) as z:providers[n]=[x for x in z.namelist() if x=='META-INF/services/java.sql.Driver']
assert all(not x for x in providers.values())
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),sourceInverse=ref(cp),expectedTests=8,newDefinitions=4,necessaryPriorDefinitions=4,physicalClasses=186,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,pmdRaw0=0,rootNullAwayFresh=True,sameGroupInitialRootCompile=ref(rootp),afterFixtureStyleFixMainRecompile=False,originalBoundary4ByteExact=True,independentExpectedExpandedByteExact=True,declaredTargets=src['targets'],manualSuppressionAdded=False,currentClasspathSqlDriverDescriptors=providers,pureDataNoJdbcGetterOrBackendScope=True,sdkJvmNativeHostFsActivityUnmeasured=True,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
o.mkdir();(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=8,Main10RootFreshWithinGroup=True,MainRecompileAfterFixtureFix=False,physical=186,staticRaw=0)))
