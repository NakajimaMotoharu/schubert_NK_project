"""Log projections whole16 current closure; per-site standalone worker findings; no startup."""
from pathlib import Path
import datetime,hashlib,json,zipfile
import pgpt_closed_host_stages as policy
from pgpt_spotbugs_contract import checked_command
from classfile_code_metadata import decode
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG38050-unit-state-pure-after-prepare-v1/manifest.json';sp=b/'evidence/PG38052-unit-state-pure-after-static-v1/manifest.json';p=ld(pp);s=ld(sp);assert p['actualExit']==s['actualExit']==0 and p['expectedTests']==7 and len(p['mainClassHashes'])==4 and len(p['physicalClassHashes'])==4
assert p['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items());assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values());assert all(v['actualExit']==(4 if n=='pmd' else 0) and not v['timedOut'] for n,v in s['stages'].items());assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][n]==0 for n in ['bugs','missing','errors']);assert {x.replace('.','/')+'.class' for x in s['spotbugs']['classStats']}==set(p['mainClassHashes']);assert checked_command(s['stages']['spotbugs']['command'])==s['stages']['spotbugs']['command']
work=r.parent/'pgpt-runs/PG379/pg38050-unit-state-pure-after-v1';assert all(sha(work/'component'/n)==h for n,h in p['physicalClassHashes'].items());assert all(sha(work/'test-classes'/n)==h for n,h in p['testClassHashes'].items());anchors=[]
for row in s['rawFindings']:
 path=str(Path(row['path']).relative_to(r));line=int(row['line']);text=(r/path).read_text().splitlines()[line-1].strip();name=Path(path).name
 if row['rule']=='AvoidAccessibilityAlteration':
  assert name=='UnitStateParserNamespaceContractTest.java' and text=='constructor.setAccessible(before);'
  reason='Exactly one non-secret byteparser namespace constructor. This finally restores the exact captured false flag after asserting forbidden construction. No arbitrary type, key, OS/app authority or actual stop operation. Subsequent assertion verifies access false, no rule suppression.'
 elif row['rule']=='CloseResource':
  assert name=='UnitStateParserBytePortTest.java' and text=='var executor = Executors.newFixedThreadPool(2);'
  reason='Fixture-owned2worker/32task memory byte projections, every Future.get10seconds and finally shutdownNow/awaitTermination10seconds assertion. Exact owned executor is closed after all exits, no server/Root/native resource.'
 elif row['rule']=='DoNotUseThreads':
  assert name=='UnitStateParserBytePortTest.java'
  reason='Standalone JUnit checks32 independent literal byte projections with2 local workers. Future10/finallyshutdownNow/await10 are finite, not a J2EE component or actual state acquisition. No external process/command/Root/authority actions.'
 else:raise AssertionError(('unclassified',row))
 anchors.append(dict(path=path,rule=row['rule'],sourceAnchor=text,sourceLine=line,occurrences=1,message=row['message'],reason=reason,disposition='NOT_APPLICABLE'))
classified=policy.classify_source_findings(p['apiMainSources']+p['apiTestSources'],anchors,s['rawFindings'],lambda n:(r/n).read_text());assert len(classified)==6
providers={}
for n,h in p['dependencies'].items():
 assert sha(Path(n))==h
 with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values());metadata={n[:-6]:decode((work/'component'/n).read_bytes(),n) for n in p['mainClassHashes']};assert len(metadata)==4 and all(any(m['hasCode'] for m in v['methods']) for v in metadata.values());targets=sorted(n for n in metadata if n.endswith('/UnitStateParser'));assert len(targets)==1
out=b/'evidence/PG38056-unit-state-pure-admission-v1';assert not out.exists();out.mkdir();counts={n:6 if Path(n).name=='UnitStateParserBytePortTest.java' else 1 for n in p['apiTestSources']};assert len(counts)==2 and sum(counts.values())==7;testnames=set(p['apiTestSources']);assert len(p['expectedCases'])==7;abi=ld(b/'evidence/PG38054-unit-state-abi-body-inverse-v1/manifest.json');assert abi['actualExit']==0 and abi['originalWhole6BusinessBodyInverseExact'] and all(x['allVisibilityAbiEqual'] and x['privateGuardOnlyInverseExact'] for x in abi['rows'])
normal=dict(actualExit=0,sourceCore='5d691dcd34aff54f5c67366dd1414ed1ee5b3699',work=str(work),mainInputHashes={n:h for n,h in p['inputHashes'].items() if n not in testnames},testSourceHashes={n:h for n,h in p['inputHashes'].items() if n in testnames},physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],toolDependencyHashes=p['dependencies'],classpath=':'.join([str(work/'component'),*p['dependencies']]),wholeTestSourceCounts=counts,expectedCases=p['expectedCases'],expectedTests=7,originalPrepare=ref(pp),static=ref(sp));np=out/'normalized-prepare.json';np.write_text(json.dumps(normal,indent=2)+'\n');value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,classified=classified,declaredTargets=targets,mainMethodInventory=metadata,RootNullAwayMain4=True,explicitMaxLowPhysical4=True,classpathSqlDriverDescriptors=providers,wholeFixtureCounts=counts,newDefinitions=1,originalDefinitions=6,originalWhole6BusinessBodyInverseExact=True,actualRootVmDbNativeKeyAuthorityActions=0,newProductTests=0,formalUpdated=False,newAcceptance=0);(out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n');print(dict(actualExit=0,classified=6,CodeTargets=1,CodeMethods=sum(m['hasCode'] for n in targets for m in metadata[n]['methods']),allPhysical=4,expectedTests=7))
