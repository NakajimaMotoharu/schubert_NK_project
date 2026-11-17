"""Per-site static admission, original Main compile/SB by exact15 bytes, all191 dependency bindings."""
from pathlib import Path
import datetime, hashlib, json, zipfile
import pgpt_closed_host_stages as policy

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; w=r.parent/'pgpt-runs/PG379/pg37730-web-monitoring41-final-v3'
load=lambda p:json.loads(p.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37730-web-monitoring41-final-prepare-v3/manifest.json'; sp=b/'evidence/PG37732-web-monitoring41-final-static-v3/manifest.json'
p=load(pp); st=load(sp); source=load(b/'evidence/PG37714-web-monitoring-family-source-v1/manifest.json')
assert p['actualExit']==st['actualExit']==0 and p['expectedTests']==41 and p['newDefinitions']==11 and p['necessaryPriorDefinitions']==30
assert p['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items())
assert len(p['physicalClassHashes'])==191 and len(p['mainClassHashes'])==15
assert not st['processingErrors'] and st['checkstyleFindings']==0
assert all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert {n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}==set(p['mainClassHashes'])
assert st['spotbugsReuse']['same15ActualMainClassBytes'] and st['spotbugsReuse']['sameSdkHashes']
assert p['originalMainNullAwayStage']['actualExit']==0 and not p['originalMainNullAwayStage']['timedOut']
for n,h in p['physicalClassHashes'].items():assert sha(w/'component'/n)==h
for n,h in p['testClassHashes'].items():assert sha(w/'test-classes'/n)==h
assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values())
assert all(v['actualExit']==(4 if k=='pmd' else 0) and not v['timedOut'] for k,v in st['stages'].items())
anchors=[]
for row in st['rawFindings']:
    path=str(Path(row['path']).relative_to(r)); line=int(row['line']); text=(r/path).read_text().splitlines()[line-1].strip()
    if row['rule']=='DoNotUseThreads':
        reason=f'{Path(path).stem}: standalone bounded JUnit concurrency fixture, not a J2EE-managed component. Source uses finite invokeAll/get followed by finally shutdownNow and awaitTermination(10 seconds); pool size4/8 and tasks64 are fixed, no app/DB/VM workers.'
    elif row['rule']=='CloseResource':
        reason=f'{Path(path).stem}: this exact ExecutorService local is owned and closed by the method finally shutdownNow/awaitTermination(10 seconds) plus an explicit termination assertion. ExecutorService.close is intentionally avoided because it waits without a deadline.'
    elif row['rule']=='CompareObjectsWithEquals':
        assert Path(path).name=='WebDbPoolMetricRecorderTest.java' and 'actual == first || actual == second' in text
        reason='The atomic publication fixture requires the reader to observe one of the exact two supplied immutable snapshot objects, not a newly copied or mixed record. Reference identity is the condition under test; value equality would weaken this guarantee.'
    elif row['rule']=='EqualsNull':
        reason='This explicit false equals(null) call verifies the public immutable record Object.equals null contract, alongside same/different component and wrong-type cases. It is a negative assertion in a fixture, not production null detection.'
    elif row['rule']=='NullAssignment':
        reason='This assignment deliberately poisons a fixture-owned array: old outbox Duration elements verify null constructor rejection; new values array verifies caller mutation never changes enum storage or another returned array. No application field or shared state receives null.'
    elif row['rule']=='UseConcurrentHashMap':
        assert Path(path).name=='MediaBytesMetricRecorderTest.java'
        reason='This expected Map is populated only by the single JUnit owner while constructing the task list, before invokeAll publishes tasks. Workers mutate the recorder, not this oracle; assertions read the map only after every bounded future has completed. No concurrent map writes exist.'
    else:raise AssertionError(('unclassified',row))
    anchors.append(dict(path=path,rule=row['rule'],sourceAnchor=text,sourceLine=line,occurrences=1,message=row['message'],reason=reason,disposition='NOT_APPLICABLE'))
# Two identity comparisons share one source line and one rule message; preserve multiplicity.
grouped={}
for a in anchors:
    key=(a['path'],a['rule'],a['sourceLine'],a['message'])
    if key in grouped:grouped[key]['rawMultiplicity']=grouped[key].get('rawMultiplicity',1)+1
    else:grouped[key]=a
classified=policy.classify_source_findings(p['apiMainSources']+p['apiTestSources'],list(grouped.values()),st['rawFindings'],lambda n:(r/n).read_text())
assert len(classified)==len(st['rawFindings'])==30
providers={}
for n,h in p['dependencies'].items():
    assert sha(Path(n))==h
    with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values())
out=b/'evidence/PG37734-web-monitoring41-admission-v1';assert not out.exists();out.mkdir()
counts={n:sum(x['classname']==n.split('/src/test/java/')[1][:-5].replace('/','.') for x in p['expectedCases']) for n in p['apiTestSources']}
assert sorted(counts.values())==[6,8,8,8,11]
normal=dict(actualExit=0,sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',work=str(w),
    mainInputHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' not in n},testSourceHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' in n},
    physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],toolDependencyHashes=p['dependencies'],
    classpath=':'.join([str(w/'component'),*p['dependencies']]),wholeTestSourceCounts=counts,expectedTests=41,originalPrepare=ref(pp),static=ref(sp))
np=out/'normalized-prepare.json';np.write_text(json.dumps(normal,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,classified=classified,
    originalMainCompileAndSpotbugsReusedNotReplayed=True,all15ActualMainBytesVerified=True,all191PhysicalNamesVerified=True,
    declaredTargets=sorted(n[:-6] for n in p['mainClassHashes'] if not n.endswith('/package-info.class')),
    classpathSqlDriverDescriptors=providers,sources41WholeCases=counts,actualRootVmDbNativeKeysAuthorityActions=0,newTestsExecuted=0,formalUpdated=False,newAcceptance=0)
assert len(v['declaredTargets'])==14
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,Main5Static15All0=True,classified=30,expectedTests=41,targets=14,physical=191))
