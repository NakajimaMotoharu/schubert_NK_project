"""Admit nine concrete memory-servlet fixture sites and freshRoot seven safe Web Main sources."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34746-ssc435-aad5-prepare-v1/manifest.json';sp=b/'evidence/PG34748-ssc435-aad5-static-v1/manifest.json';cp=b/'evidence/PG34744-ssc435-aad-source-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);proof=ld(cp);out=b/'evidence/PG34750-ssc435-aad5-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==proof['actualExit']==0 and m['expectedTests']==5 and len(m['apiMainSources'])==5 and len(m['apiTestSources'])==2;assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==st['spotbugs']['errors']==st['spotbugs']['missing']==0;assert proof['oldExceptionOneByteExact'] and proof['onlyMainProtectedAcquisitionInverseFormattedExact'] and proof['allFieldAcquisitionInsideCleanupRegion'] and proof['sixEmptyNonnullSlotShapeBeforeTry'] and proof['originalSixExpressionsAndOrderPreserved'] and proof['allOriginalFiveTestsByteExact'] and proof['independentAad']['length']==113 and st['rawFindings']==[];classified=[]
work=r.parent/'pgpt-runs/PG379/pg34746-ssc435-aad5-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==182 and len(m['mainClassHashes'])==6 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(p))==h for p,h in m['dependencies'].items());providers={}
for p in m['dependencies']:
 with zipfile.ZipFile(p) as z:providers[p]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
assert all(not values for values in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=5,newDefinitions=0,necessaryPriorDefinitions=5,physicalClasses=182,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,rootNullAwayFresh=True,originalException1ByteExact=True,sourceInverse=ref(cp),currentTransformation="PROTECTED_SIX_FIELD_ACQUISITION_INVERSE_EXACT",inheritedHelperInverseFlagDescribesPriorSourceOnly="PG34704/SSC434/Coreeaea0c45",pmdRaw0=0,classified=classified,declaredTargets=proof['targets'],manualSuppressionAdded=False,currentClasspathSqlDriverDescriptors=providers,pureValueNoJdbcOrBackendScope=True,explicitSdkHashes=proof['sdkHashes'],actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=5,physical=182,rootMain5Fresh=True,staticRaw=0,applicable=0,spotbugs=0)))
