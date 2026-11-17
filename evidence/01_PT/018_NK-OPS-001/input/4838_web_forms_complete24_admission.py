"""Same current source/byte closure, per-site static reasons, full qualified Main reuse, no runtime."""
from pathlib import Path
import datetime,hashlib,json,zipfile
import pgpt_closed_host_stages as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37852-web-forms-complete24-prepare-v2/manifest.json';sp=b/'evidence/PG37854-web-forms-complete24-static-v1/manifest.json';p=ld(pp);s=ld(sp);assert p['actualExit']==s['actualExit']==0 and p['expectedTests']==24 and len(p['mainClassHashes'])==19 and len(p['physicalClassHashes'])==195
assert p['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items())
assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values());assert all(v['actualExit']==(4 if n=='pmd' else 0) and not v['timedOut'] for n,v in s['stages'].items())
assert not s['processingErrors'] and s['checkstyleFindings']==0 and s['spotbugsReuse']['allCurrent195BytesAnalyzedBefore'] and s['spotbugsReuse']['explicitMaxLowFailOnError'] and s['spotbugsReuse']['bugMissingError0']
work=Path(p['work']);assert all(sha(work/'component'/n)==h for n,h in p['physicalClassHashes'].items());assert all(sha(work/'test-classes'/n)==h for n,h in p['testClassHashes'].items())
anchors=[]
for row in s['rawFindings']:
 path=str(Path(row['path']).relative_to(r));line=int(row['line']);text=(r/path).read_text().splitlines()[line-1].strip()
 if row['rule']=='CloseResource':
  assert Path(path).name in ['ScenarioSearchFormTest.java','LogSearchFormTest.java'] and 'newFixedThreadPool(8)' in text
  reason='This exact fixture-local pool is owned by finally shutdownNow and awaitTermination(10 seconds) with termination assertion. All64 task futures use get(10 seconds); TWR indefinite close was already replaced, no application worker or shared pool is created.'
 elif row['rule']=='DoNotUseThreads':
  assert Path(path).name in ['ScenarioSearchFormTest.java','LogSearchFormTest.java']
  reason='Standalone JUnit exercises64 independent binds on8 fixture-owned workers and validates exact per-request values. It is not a J2EE-managed component; every future wait and final executor termination is finite10seconds, no production server/background job is started.'
 elif row['rule']=='NullAssignment':
  assert Path(path).name=='WebPublicEnumContractTest.java' and 'first[0] = null;' in text
  reason='The caller-owned returned values array is deliberately poisoned to prove enum backing storage and future returned arrays are unchanged. This is an explicit independent copy-isolation negative contract, not a production null assignment.'
 else:raise AssertionError(('unclassified',row))
 anchors.append(dict(path=path,rule=row['rule'],sourceAnchor=text,sourceLine=line,occurrences=1,message=row['message'],reason=reason,disposition='NOT_APPLICABLE'))
classified=policy.classify_source_findings(p['apiMainSources']+p['apiTestSources'],anchors,s['rawFindings'],lambda n:(r/n).read_text());assert len(classified)==11
providers={}
for n,h in p['dependencies'].items():
 assert sha(Path(n))==h
 with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values())
stems=['dev/codex/schubert/nk/web/'+n for n in ['form/ScenarioSearchForm','form/LogSearchForm','view/ErrorViewModel','view/MenuCard','revocation/RevocationFailureCode','logging/WebHttpLogKind']];targets=sorted(n[:-6] for n in p['mainClassHashes'] if any(n==stem+'.class' or n.startswith(stem+'$') for stem in stems));assert len(targets)==11
out=b/'evidence/PG37856-web-forms-complete24-admission-v1';assert not out.exists();out.mkdir();counts={n:sum(x['classname']==n.split('/src/test/java/')[1][:-5].replace('/','.') for x in p['expectedCases']) for n in p['apiTestSources']};assert sorted(counts.values())==[8,8,8]
normal=dict(actualExit=0,sourceCore=p['sourceCore'],work=p['work'],mainInputHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' not in n},testSourceHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' in n},physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],toolDependencyHashes=p['dependencies'],classpath=':'.join([str(work/'component'),*p['dependencies']]),wholeTestSourceCounts=counts,expectedCases=p['expectedCases'],expectedTests=24,originalPrepare=ref(pp),static=ref(sp))
np=out/'normalized-prepare.json';np.write_text(json.dumps(normal,indent=2)+'\n');v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,classified=classified,declaredTargets=targets,formSixTargets=[n for n in targets if '/form/' in n],MainCompileAndMaxLow195ReusedNotReplayed=True,Main14Source19BytesQualified=True,classpathSqlDriverDescriptors=providers,wholeFixtureCounts=counts,newDefinitions=0,actualRootVmDbNativeKeyAuthorityActions=0,newProductTests=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,classified=11,targets=11,formTargets=6,physical195=195,expected24=24,wholeFixture3=True))
