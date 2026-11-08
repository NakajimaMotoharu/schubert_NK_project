"""Seven original pure view whole64: raw-exact inverse edits including text blocks, typed full coverage."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,xml.etree.ElementTree as E,shutil,zipfile
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/062_pure_view_seven_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24370-pure-view-seven-bounded-sixtyfour-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,64,0,0,0)
assert begin['source']=='ed2e968a8381c491ba8df6986e59d48afb0b9c0f' and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert begin['expectedTests']==64 and begin['newMethods']==0 and begin['requalifiedExistingMethods']==64
for path,pin in begin['inputHashes'].items():assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,h in begin['dependencies'].items():assert sha(Path(path))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==7 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(cfg['declarationRegex'], (R/path).read_text())};assert len(expected)==64
cases=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+t) for t in ['failure','error','skipped'])
 for x in tree.findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),seconds=x.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==64 and {(x['classname'],x['name']) for x in cases}==expected
for text in ['64 tests found','64 tests started','64 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['allOriginalOtherTokensAndOraclesPreserved'] and pf['noFixtureOrMethodExtraction'] and pf['originalWholeMethods']==64
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(35,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256'] and sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Raw exact inverse, not token normalization: Page has a text block whose bytes must be preserved.
before_meta=load(R/cfg['beforeMetadataPath']);metarows={v['path']:v for v in before_meta['originalWholeTestSources']};inverse_rows=[]
for path in cfg['testClasses']:
 row=metarows[path];var=row['poolVariable'];original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(original).hexdigest()==row['sourceSha256']
 text=(R/path).read_text();a='var '+var+' = Executors.newFixedThreadPool(8);\n    try {';b='} finally {\n      '+var+'.shutdownNow();\n      assertTrue('+var+'.awaitTermination(10, TimeUnit.SECONDS));\n    }'
 assert text.count(a)==text.count(b)==1;text=text.replace(a,'try (var '+var+' = Executors.newFixedThreadPool(8)) {',1).replace(b,'}',1);assert text.encode()==original
 inverse_rows.append(dict(path=path,beforeSha256=row['sourceSha256'],rawExactInverse=True,allOtherWhitespaceAndStringLiteralBytesPreserved=True,textBlockPresent='"""' in original.decode()))
assert len(inverse_rows)==7
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256'];physical=cfg['currentMainPhysical'];assert len(physical)==24 and physical==m['physical']==pf['physical']
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
for key,value in [('LINE',498),('METHOD',203),('CLASS',24),('BRANCH',138)]:assert coverage[key]==dict(covered=value,missed=0)
assert all(int(x.get('missed'))==0 for c in classes.values() for x in c.findall('counter'))
individual={};natural_zero=[]
for source in tree.findall('.//sourcefile'):
 name=source.get('name');counters={c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in source.findall('counter')}
 assert all(v['missed']==0 for v in counters.values())
 if 'BRANCH' not in counters:
  natural_zero.append(name);counters['BRANCH']=dict(covered=0,missed=0,rate=None,status='NATURAL_ZERO_NOT_100_PERCENT')
 individual[name]=counters
assert set(individual)=={Path(v).name for v in cfg['mainPaths']} and len(individual)==11

O.mkdir();suite=E.Element('testsuite',name='PG24368_PURE_VIEW_SEVEN_WHOLE64',tests='64',failures='0',errors='0',skipped='0')
for x in cases:E.SubElement(suite,'testcase',classname=x['classname'],name=x['name'],time=x['seconds'])
E.ElementTree(suite).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],sourceMainUnchanged=True,tests=64,testClasses=7,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=64,newUniqueTests=0,sourcePrograms=11,physicalClasses=24,coverage=coverage,wholeTargetLmc100=True,naturalZeroBranchSourceNames=natural_zero,individualSourceCounters=individual,aggregateBranchRate=100,branchStatus='ALL_APPLICABLE_CONDITIONS_138_COVERED_INDIVIDUAL_NATURAL_ZERO_NA',aggregateApplicableFour100=True,allSourcesNonemptyFour100=not bool(natural_zero),strictNonemptyFour100GateExit=1 if natural_zero else 0,allOriginalOtherTokensAndOraclesPreserved=True,independentInverseSourceRecipeVerified=True,originalFutureGetBoundsSeconds=10,sevenFixedPoolTerminationBoundsSeconds=10,rawExactInverseRows=inverse_rows,allOriginalAnnotationsAndTextBlocksUnchanged=True,normalOwnerTerminationAsserted=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=35,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,manualCoverageExclusions=[],oldExecUnion=False,singleSession=cfg['session'],actualBackendOrRootVmNativeKeyOperations=False,noOriginalMethodExtractionOrSubstitute=True,reportedEnvironment=env,caseTimings=cases,originalXmlPins=pins,productTestsExecuted=64,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,globalYkt2177Accepted=False,bugs=['BUG-2531'],ykts=['YKT-2177'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=64,coverage=coverage,aggregateBranchRate=100,naturalZeroSources=natural_zero,strictSourceNonemptyFour100Gate=1 if natural_zero else 0,observedMain=len(positive),heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
