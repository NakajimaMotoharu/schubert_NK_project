"""Six original form whole56: raw-exact bounded invokeAll/owner edits, all actual counters and sealed ABI."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,xml.etree.ElementTree as E,shutil,zipfile
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/067_web_six_form_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24396-web-six-form-bounded-fiftysix-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,56,0,0,0)
assert begin['source']=='2dd95b08fd3d03307a4a3d26ba7eeef824b640c3' and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert begin['expectedTests']==56 and begin['newMethods']==0 and begin['requalifiedExistingMethods']==56
for path,pin in begin['inputHashes'].items():assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,h in begin['dependencies'].items():assert sha(Path(path))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==6 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(cfg['declarationRegex'], (R/path).read_text())};assert len(expected)==56
cases=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+t) for t in ['failure','error','skipped'])
 for x in tree.findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),seconds=x.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==56 and {(x['classname'],x['name']) for x in cases}==expected
for text in ['56 tests found','56 tests started','56 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['allOriginalOtherBytesAndOraclesPreserved'] and pf['noFixtureOrMethodExtraction'] and pf['originalWholeMethods']==56
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(34,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256'] and sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Raw exact inverse, not token normalization: Page has a text block whose bytes must be preserved.
before_meta=load(R/cfg['beforeMetadataPath']);metarows={v['path']:v for v in before_meta['originalWholeTestSources']};inverse_rows=[]
for path in cfg['testClasses']:
 row=metarows[path];var=row['poolVariable'];original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(original).hexdigest()==row['sourceSha256']
 text=(R/path).read_text();a='var '+var+' = Executors.newFixedThreadPool(8);\n    try {';b='} finally {\n      '+var+'.shutdownNow();\n      assertTrue('+var+'.awaitTermination(10, TimeUnit.SECONDS));\n    }'
 assert text.count(a)==text.count(b)==1;text=text.replace(a,'try (var '+var+' = Executors.newFixedThreadPool(8)) {',1).replace(b,'}',1)
 if row['invokeAllBoundAdded']:
  statement='for (var future : executor.invokeAll(tasks, 30, TimeUnit.SECONDS))\n        future.get(30, TimeUnit.SECONDS);';assert text.count(statement)==1;text=text.replace(statement,'for (var future : executor.invokeAll(tasks)) future.get(30, TimeUnit.SECONDS);',1)
 assert text.encode()==original
 inverse_rows.append(dict(path=path,beforeSha256=row['sourceSha256'],rawExactInverse=True,allOtherWhitespaceAndStringLiteralBytesPreserved=True,textBlockPresent='"""' in original.decode()))
assert len(inverse_rows)==6
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256'];physical=cfg['currentMainPhysical'];assert len(physical)==16 and physical==m['physical']==pf['physical']
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
for key,value in [('LINE',544),('METHOD',122),('CLASS',16),('BRANCH',278)]:assert coverage[key]==dict(covered=value,missed=0)
assert all(int(x.get('missed'))==0 for c in classes.values() for x in c.findall('counter'))
raw_class_rows={v[6]:v for v in re.findall(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(U/'classinfo.stdout').read_text(),re.M)}
assert set(raw_class_rows)==set(physical)
individual={};natural_zero=[]
for source in tree.findall('.//sourcefile'):
 name=source.get('name');counters={c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in source.findall('counter')}
 assert all(v['missed']==0 for v in counters.values())
 if 'BRANCH' not in counters:
  matching=[n for n in physical if Path(index[n]['path']).name==name];assert matching and all(int(raw_class_rows[n][1])==0 and raw_class_rows[n][5]==index[n]['crc64'] for n in matching)
  natural_zero.append(name);counters['BRANCH']=dict(covered=0,missed=0,rate=None,status='NATURAL_ZERO_CONFIRMED_ACTUAL_CLASSINFO_NOT_100_PERCENT')
 individual[name]=counters
assert set(individual)=={Path(v).name for v in cfg['mainPaths']} and len(individual)==12

interface=pf['noCodeInterface'];assert interface['abstractMethods']==5 and interface['codeMethods']==0 and interface['coverageRate'] is None
assert interface['path']==cfg['noCodeInterface'] and sha(R/interface['path'])==interface['sourceSha256']
with zipfile.ZipFile(normal['jars']['web']['path']) as z:
 name='dev/codex/schubert/nk/web/form/UserChangeForm.class';assert hashlib.sha256(z.read(name)).hexdigest()==interface['physicalSha256']
assert 'dev/codex/schubert/nk/web/form/UserChangeForm' not in classes and 'dev/codex/schubert/nk/web/form/UserChangeForm' not in positive
O.mkdir();suite=E.Element('testsuite',name='PG24394_WEB_SIX_FORMS_WHOLE56',tests='56',failures='0',errors='0',skipped='0')
for x in cases:E.SubElement(suite,'testcase',classname=x['classname'],name=x['name'],time=x['seconds'])
E.ElementTree(suite).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],sourceMainUnchanged=True,tests=56,testClasses=6,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=56,newUniqueTests=0,sourcePrograms=12,physicalClasses=16,coverage=coverage,wholeTargetLmc100=True,metadataSourcePrograms=1,noCodeInterface=interface,interfaceArtificialClassCoverageAdded=False,naturalZeroBranchSourceNames=natural_zero,individualSourceCounters=individual,aggregateBranchRate=100,branchStatus='ALL_APPLICABLE_CONDITIONS_278_COVERED_INDIVIDUAL_NATURAL_ZERO_NA',aggregateApplicableFour100=True,allSourcesNonemptyFour100=not bool(natural_zero),strictNonemptyFour100GateExit=1 if natural_zero else 0,allOriginalOtherTokensAndOraclesPreserved=True,independentInverseSourceRecipeVerified=True,originalFutureGetBoundsSeconds=10,sixFixedPoolTerminationBoundsSeconds=10,singleInvokeAllBoundSeconds=30,originalFuture5TenThirtyBoundsUnchanged=True,rawExactInverseRows=inverse_rows,allOriginalAnnotationsAndStringBytesUnchanged=True,normalOwnerTerminationAsserted=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=34,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,manualCoverageExclusions=[],oldExecUnion=False,singleSession=cfg['session'],actualBackendOrRootVmNativeKeyOperations=False,noOriginalMethodExtractionOrSubstitute=True,reportedEnvironment=env,caseTimings=cases,originalXmlPins=pins,productTestsExecuted=56,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,globalYkt2177Accepted=False,bugs=['BUG-2532'],ykts=['YKT-2177'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=56,coverage=coverage,aggregateBranchRate=100,naturalZeroSources=natural_zero,strictSourceNonemptyFour100Gate=1 if natural_zero else 0,observedMain=len(positive),heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
