"""Question form1/Test1 current Root quality and per-site PMD disposition; no runtime."""
from pathlib import Path
import datetime,hashlib,json,zipfile
import pgpt_closed_host_stages as policy
from pgpt_spotbugs_contract import checked_command
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37884-question-form-prepare-v1/manifest.json';sp=b/'evidence/PG37886-question-form-static-v1/manifest.json';p=ld(pp);s=ld(sp);assert p['actualExit']==s['actualExit']==0 and p['expectedTests']==8 and len(p['mainClassHashes'])==1 and len(p['physicalClassHashes'])==177
assert p['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items());assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values());assert all(v['actualExit']==(4 if n=='pmd' else 0) and not v['timedOut'] for n,v in s['stages'].items())
assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][n]==0 for n in ['bugs','missing','errors']);assert s['spotbugs']['classStats']==['dev.codex.schubert.nk.web.form.QuestionSubmitForm'];assert checked_command(s['stages']['spotbugs']['command'])==s['stages']['spotbugs']['command']
work=r.parent/'pgpt-runs/PG379/pg37884-question-form-v1';assert all(sha(work/'component'/n)==h for n,h in p['physicalClassHashes'].items());assert all(sha(work/'test-classes'/n)==h for n,h in p['testClassHashes'].items())
anchors=[]
for row in s['rawFindings']:
 path=str(Path(row['path']).relative_to(r));line=int(row['line']);text=(r/path).read_text().splitlines()[line-1].strip();assert path.endswith('/QuestionSubmitFormTest.java')
 if row['rule']=='CloseResource':
  assert text=='var executor = Executors.newFixedThreadPool(8);';reason='This exact fixture-local pool is owned by finally shutdownNow and asserted awaitTermination(10seconds). All100 independent task futures use get(30seconds). No managed application executor/server/resource is created; finite cleanup replaces indefinite TWR.'
 elif row['rule']=='DoNotUseThreads':
  assert line in [238,244,265,266];reason='Standalone JUnit verifies100 independent request bodies/UUID syntax on8 fixture-owned workers. Every future wait30seconds and finally termination10seconds is finite. This fixture is not a J2EE-managed application component.'
 else:raise AssertionError(('unclassified',row))
 anchors.append(dict(path=path,rule=row['rule'],sourceAnchor=text,sourceLine=line,occurrences=1,message=row['message'],reason=reason,disposition='NOT_APPLICABLE'))
classified=policy.classify_source_findings(p['apiMainSources']+p['apiTestSources'],anchors,s['rawFindings'],lambda n:(r/n).read_text());assert len(classified)==5
providers={}
for n,h in p['dependencies'].items():
 assert sha(Path(n))==h
 with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values());targets=sorted(n[:-6] for n in p['mainClassHashes']);assert targets==['dev/codex/schubert/nk/web/form/QuestionSubmitForm']
proto=b/'evidence/PG37784-pure-protocol-web-maxlow-static-v1/manifest.json';v=ld(proto);assert v['actualExit']==0 and v['spotbugsMaxLowExplicit'] and v['classStatsSetExact'];assert all(v['physicalClassHashes'][n]==h for n,h in p['physicalClassHashes'].items() if n not in p['mainClassHashes'])
out=b/'evidence/PG37888-question-form-current8-admission-v1';assert not out.exists();out.mkdir();counts={p['apiTestSources'][0]:8};normal=dict(actualExit=0,sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',work=str(work),mainInputHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' not in n},testSourceHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' in n},physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],toolDependencyHashes=p['dependencies'],classpath=':'.join([str(work/'component'),*p['dependencies']]),wholeTestSourceCounts=counts,expectedCases=p['expectedCases'],expectedTests=8,originalPrepare=ref(pp),static=ref(sp));np=out/'normalized-prepare.json';np.write_text(json.dumps(normal,indent=2)+'\n');value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,classified=classified,declaredTargets=targets,RootNullAwayMain1=True,explicitMaxLowMain1=True,currentProtocol176MaxLowReuse=ref(proto),classpathSqlDriverDescriptors=providers,wholeFixtureCounts=counts,newDefinitions=0,actualRootVmDbNativeKeyAuthorityActions=0,newProductTests=0,formalUpdated=False,newAcceptance=0);(out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n');print(dict(actualExit=0,classified=5,targets=1,allPhysical=177,expectedTests=8))
