"""Explicit same-source static/ABI/dependency admission; no application or prior Test replay."""
from pathlib import Path
import datetime, hashlib, json, zipfile
import pgpt_closed_host_stages as static_policy

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; w=r.parent/'pgpt-runs/PG379/pg37692-web-enum-eight-v1'
load=lambda p:json.loads(p.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37692-web-enum-eight-prepare-v1/manifest.json'
sp=b/'evidence/PG37696-web-enum-eight-static-v2/manifest.json'
p=load(pp); st=load(sp); closure=load(b/'evidence/PG37690-web-enum-eight-source-closure-v1/manifest.json')
assert p['actualExit']==st['actualExit']==0 and p['expectedTests']==p['newDefinitions']==8 and p['necessaryPriorDefinitions']==0
assert p['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items())
assert not st['processingErrors'] and st['checkstyleFindings']==0
assert all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert {x.replace('.','/')+'.class' for x in st['spotbugs']['classStats']}==set(p['mainClassHashes'])
assert len(p['physicalClassHashes'])==194 and len(p['mainClassHashes'])==18
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
    assert {n:sha(w/folder/n) for n in p[key]}==p[key]
for dep,h in p['dependencies'].items(): assert sha(Path(dep))==h
anchor=dict(path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/WebPublicEnumContractTest.java',
    rule='NullAssignment',sourceAnchor='first[0] = null; // Poison a caller-owned array to prove enum storage remains unmodified.',
    occurrences=1,reason='This test intentionally poisons its caller-owned values array, then checks both a prior independent array and a newly returned array retain the original constant. Null is a deliberate negative alias probe in a test-local array, never application state or a production assignment.',disposition='NOT_APPLICABLE')
classified=static_policy.classify_source_findings(p['apiMainSources']+p['apiTestSources'],[anchor],st['rawFindings'],lambda n:(r/n).read_text())
assert len(classified)==1
assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values())
assert all(v['actualExit']==(4 if k=='pmd' else 0) and not v['timedOut'] for k,v in st['stages'].items())
old=load(b/'evidence/PG37462-principal-current8-prepare-v1/manifest.json')
retained={n:p['mainClassHashes'][n]==h for n,h in old['mainClassHashes'].items()}
assert len(retained)==7 and all(retained.values())
providers={}
for name in p['dependencies']:
    with zipfile.ZipFile(name) as z:providers[name]='META-INF/services/java.sql.Driver' in z.namelist()
assert not any(providers.values())
out=b/'evidence/PG37698-web-enum-eight-admission-v1'; assert not out.exists(); out.mkdir()
tests={n:sum(x['classname']==n.split('/src/test/java/')[1][:-5].replace('/','.') for x in p['expectedCases']) for n in p['apiTestSources']}
assert list(tests.values())==[8]
normal=dict(actualExit=0,sourceCore=closure['scopeSourceCore'],work=str(w),
    mainInputHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' not in n},
    testSourceHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' in n},
    physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],
    toolDependencyHashes=p['dependencies'],classpath=':'.join([str(w/'component'),*p['dependencies']]),
    wholeTestSourceCounts=tests,expectedTests=8,originalPrepare=ref(pp),static=ref(sp))
np=out/'normalized-prepare.json'; np.write_text(json.dumps(normal,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),
    originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,
    classified=classified,spotbugsFullMainPhysical18=True,originalRootNullAwayConfiguration=True,
    previousPrincipal7ClassBytesExact=retained,previousPrincipal8Replayed=False,previousProtocol156Replayed=False,
    declaredTargets=closure['targetClasses'],all194PhysicalClassnamesAdmitted=True,
    currentClasspathSqlDriverDescriptors=providers,wholeWebOrSixModuleAccepted=False,
    actualDbRootVmNativeKeyAuthorityActions=0,newTestsExecuted=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n')
print(dict(actualExit=0,physical=194,Main13StaticApplicable0=True,expected8=tests))
