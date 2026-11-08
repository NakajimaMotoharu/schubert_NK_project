"""Original MVC template five fixtures38: finite worker before context close, isolated public IO."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,xml.etree.ElementTree as E,shutil,zipfile,sys
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/079_mvc_template_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24522-mvc-template-original-thirtyeight-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,38,0,0,0)
assert begin['source']==sys.argv[1] and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert begin['expectedTests']==38 and begin['newMethods']==0 and begin['requalifiedExistingMethods']==38
for path,pin in begin['inputHashes'].items():assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,h in begin['dependencies'].items():assert sha(Path(path))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==5 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(cfg['declarationRegex'], (R/path).read_text())};assert len(expected)==38
cases=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+t) for t in ['failure','error','skipped'])
 for x in tree.findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),seconds=x.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==38 and {(x['classname'],x['name']) for x in cases}==expected
for text in ['38 tests found','38 tests started','38 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['allOriginalOtherTokensAndOraclesPreserved'] and pf['noFixtureOrMethodExtraction'] and pf['originalWholeMethods']==38
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(26,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256'] and sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Independent inverse assembly and canonical formatter receipt validation; no formatter replay.
before_meta=load(R/cfg['beforeMetadataPath']);metarows={v['path']:v for v in before_meta['originalWholeTestSources']};pfrows={v['path']:v for v in pf['wholeOriginalTestSources']};inverse_rows=[]
for path in cfg['testClasses']:
 row=metarows[path];var=row['poolVariable'];ctx=row['contextVariable'];original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(original).hexdigest()==row['sourceSha256'];text=(R/path).read_text();a='    try (var '+ctx+' = context()) {\n      var '+var+' = Executors.newFixedThreadPool(8);\n      try {';b='\n      } finally {\n        '+var+'.shutdownNow();\n        assertTrue('+var+'.awaitTermination(10, TimeUnit.SECONDS));\n      }';assert text.count(a)==text.count(b)==1;i=text.index(a);j=text.index(b,i);body=text[i+len(a):j];assert '"""' not in body;lines=body.splitlines(keepends=True);restored=[]
 for line in lines:
  if line.strip():assert line.startswith('  ');restored.append(line[2:])
  else:restored.append(line)
 inverse=text[:i]+'    try (var '+ctx+' = context();\n        var '+var+' = Executors.newFixedThreadPool(8)) {'+''.join(restored)+text[j+len(b):];r=pfrows[path];assert hashlib.sha256(inverse.encode()).hexdigest()==r['inversePreformatSha256'];raw=inverse.encode()==original
 if not raw:
  assert r['rawExactInverse'] is False and r['formatterCanonicalExactInverse'] is True;f=Path(r['inverseFormatterInputPath']);assert sha(f)==r['inverseCanonicalSha256']==row['sourceSha256'];stage=pf['formatterInverseStage'];assert stage['actualExit']==0 and not stage['timedOut'];assert '--skip-reflowing-long-strings' in stage['command'] and '--replace' in stage['command'] and str(f) in stage['command'];assert sha(RUNS/cfg['inverseFormatterSlot']/'format-inverse.stdout')==stage['stdoutSha256'];assert sha(RUNS/cfg['inverseFormatterSlot']/'format-inverse.stderr')==stage['stderrSha256']
 assert sorted(set(map(int,re.findall(r'\.get\((\d+), TimeUnit.SECONDS\)',body))))==row['futureGetBoundsSeconds'];inverse_rows.append(dict(path=path,beforeSha256=row['sourceSha256'],rawExactInverse=raw,canonicalExactInverse=True,originalFutureBounds=row['futureGetBoundsSeconds'],poolTerminationBeforeContextClose=True))
assert len(inverse_rows)==5 and sum(v['rawExactInverse'] for v in inverse_rows)==4
work=U/'work';assert begin['isolatedWorkingDirectory']==str(work) and begin['existingRepositoryTargetWritten'] is False and m['stages']['unit']['cwd']==str(work);assert load(U/'unit-process.safe.json')['cwd']==str(work)
for n,h in begin['publicResourceHashes'].items():assert sha(work/'src/main/resources'/n)==h==pf['publicResourceHashes'][n]
traceExpected={
 'PT-SCR-053.txt':'templates=animation|animation-list\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRecords=50\nactualNkGate=false\n',
 'PT-SCR-071.txt':'templates=music|music-sections\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumCategories=20\nmaximumSections=100\nactualNkGate=false\n',
 'PT-SCR-024.txt':'template=scenario\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumEntries=10000\nmaximumVoices=999\nactualNkGate=false\n',
 'PT-SCR-033.txt':'template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n'}
trace=work/'target/scenario-screen-traces';assert {p.name for p in trace.iterdir()}==set(traceExpected)
for n,t in traceExpected.items():assert (trace/n).read_text()==t
assert {str(p.relative_to(work)) for p in work.rglob('*') if p.is_file()}=={'src/main/resources/'+n for n in cfg['resources']}|{'target/scenario-screen-traces/'+n for n in traceExpected}

index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256'];physical=cfg['currentMainPhysical'];assert len(physical)==1 and physical==m['physical']==pf['physical']
normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json')
with zipfile.ZipFile(normal['jars']['web']['path']) as z:
 for n,h in physical.items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==sha(U/'component'/(n+'.class'))==h==index[n]['sha256']
info={n:h for h,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert info=={n:index[n]['crc64'] for n in physical}
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+cfg['session']+'"' in ex
probes={n:[identity,int(hits),int(total)] for identity,hits,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
prefix=[v.replace('.','/') for v in cfg['testClasses'].values()];positive={n for n,v in probes.items() if v[1]>0 and n.startswith('dev/codex/schubert/nk/') and not any(n==p or n.startswith(p+'$') for p in prefix)}
assert set(physical)<=positive and all(n in index and probes[n][0]==index[n]['crc64'] for n in positive)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.split('/')[-1].split('$')[0] in held for n in positive)
initialized=re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text());assert not any(h in n for h in held for n in initialized)
tree=E.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in tree.findall('.//class')};assert set(classes)==set(physical)
coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')}
for key in ['LINE','METHOD','CLASS']:assert coverage[key]['missed']==0 and coverage[key]['covered']>0
assert coverage['CLASS']['covered']==1
branchInfo=[(int(b),h,n) for b,h,n in re.findall(r'^\s*\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+class 0x([0-9a-f]{16}) (\S+)$',(U/'classinfo.stdout').read_text(),re.M)];assert len(branchInfo)==1 and branchInfo[0][0]==0 and branchInfo[0][2] in physical and branchInfo[0][1]==index[branchInfo[0][2]]['crc64'];assert 'BRANCH' not in coverage;coverage['BRANCH']=dict(covered=0,missed=0)
assert all(int(x.get('missed'))==0 for c in classes.values() for x in c.findall('counter'))
individual={};natural_zero=[]
for source in tree.findall('.//sourcefile'):
 name=source.get('name');counters={c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in source.findall('counter')}
 assert all(v['missed']==0 for v in counters.values())
 if 'BRANCH' not in counters:
  natural_zero.append(name);counters['BRANCH']=dict(covered=0,missed=0,rate=None,status='NATURAL_ZERO_NOT_100_PERCENT')
 individual[name]=counters
assert set(individual)=={Path(v).name for v in cfg['mainPaths']} and len(individual)==1

O.mkdir();suite=E.Element('testsuite',name='PG24520_MVC_TEMPLATE_WHOLE38',tests='38',failures='0',errors='0',skipped='0')
for x in cases:E.SubElement(suite,'testcase',classname=x['classname'],name=x['name'],time=x['seconds'])
E.ElementTree(suite).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
for n in traceExpected:shutil.copyfile(trace/n,O/n)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],sourceMainUnchanged=True,tests=38,testClasses=5,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=38,newUniqueTests=0,sourcePrograms=1,physicalClasses=1,coverage=coverage,wholeTargetLmc100=True,naturalZeroBranchSourceNames=natural_zero,individualSourceCounters=individual,aggregateBranchRate=None,branchStatus='NATURAL_ZERO_BRANCH_BOUND_TO_CURRENT_CLASSINFO_NO_ARTIFICIAL100',aggregateApplicableFour100=False,allSourcesNonemptyFour100=not bool(natural_zero),strictNonemptyFour100GateExit=1 if natural_zero else 0,allOriginalOtherTokensAndOraclesPreserved=True,independentInverseSourceRecipeVerified=True,originalFutureGetBoundsSeconds=[10,20],fiveFixedPoolTerminationBoundsSeconds=10,rawExactInverseRows=inverse_rows,allOriginalAnnotationsAndTextBlocksUnchanged=True,rawExactInverseCount=4,formatterCanonicalExactInverseCount=1,contextClosedAfterWorkerTermination=True,isolatedWorkingDirectory=True,existingRepositoryTargetWritten=False,publicResourceSnapshotCount=12,traceSummaryFiles=4,mockServletOnly=True,actualHttpServerOperations=0,normalOwnerTerminationAsserted=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=26,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,manualCoverageExclusions=[],oldExecUnion=False,singleSession=cfg['session'],actualBackendOrRootVmNativeKeyOperations=False,noOriginalMethodExtractionOrSubstitute=True,reportedEnvironment=env,caseTimings=cases,originalXmlPins=pins,productTestsExecuted=38,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,globalYkt2177Accepted=False,bugs=['BUG-2540'],ykts=['YKT-2177'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=38,coverage=coverage,aggregateBranchRate=None,naturalZeroSources=natural_zero,strictSourceNonemptyFour100Gate=1 if natural_zero else 0,observedMain=len(positive),heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
