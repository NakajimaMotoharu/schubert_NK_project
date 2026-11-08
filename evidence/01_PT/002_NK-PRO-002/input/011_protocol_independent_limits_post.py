"""Pure protocol original15 plus anonymous1: independent UI233 limits, unchanged hashes, current Main counters."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,xml.etree.ElementTree as E,shutil,zipfile,sys
R=Path.cwd();B=R/'evidence/01_PT/002_NK-PRO-002';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/008_protocol_independent_limits_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24546-protocol-independent-limits-original15-new1-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,16,0,0,0)
assert begin['source']==sys.argv[1] and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert begin['expectedTests']==16 and begin['newMethods']==1 and begin['requalifiedExistingMethods']==15
for path,pin in begin['inputHashes'].items():assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,h in begin['dependencies'].items():assert sha(Path(path))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(cfg['declarationRegex'], (R/path).read_text())};assert len(expected)==16
cases=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+t) for t in ['failure','error','skipped'])
 for x in tree.findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),seconds=x.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==16 and {(x['classname'],x['name']) for x in cases}==expected
for text in ['16 tests found','16 tests started','16 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['oldLogTwelveRawRestorable'] and pf['noFixtureOrMethodExtraction'] and pf['originalMethodsPreserved']==15 and pf['plannedNewIndependentMethods']==1 and pf['totalExpectedMethods']==16
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(12,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256'] and sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Directly re-read the authoritative design bytes and the reused fixture, independently of732.
before_meta=load(R/cfg['beforeMetadataPath']);limitsRef=pf['independentLimitsManifest'];assert sha(R/limitsRef['path'])==limitsRef['sha256'];lm=load(R/limitsRef['path']);assert type(lm['actualExit']) is int and lm['actualExit']==0 and lm['productMethodInvoked'] is False and type(lm['productTestsExecuted']) is int and lm['productTestsExecuted']==0
uiPath='documents/200_UI/230_インターフェース/233_固定長電文インターフェース一覧.md';raw=subprocess.check_output(['git','show',before_meta['approvedMain']+':'+uiPath]);assert hashlib.sha256(raw).hexdigest()==before_meta['approvedDesigns'][uiPath]['sha256'];independent={}
for line in raw.decode().splitlines():
 match=re.match(r'^\|[^|]*\|\s*([QSE]) `([A-Z0-9]{8})` \| ([SAI]) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \| ([\d,]+) \|',line)
 if match:
  identity=match[2];assert identity not in independent;nums=[int(match[i].replace(',','')) for i in range(4,8)];assert 256+nums[0]+nums[1]*nums[2]==nums[3];independent[identity]=[match[1],match[3],*nums]
assert len(independent)==64 and sum(v[4]>0 for v in independent.values())==14 and sum(v[0]=='S' for v in independent.values())==31
fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/layouts-ui233.tsv';fixtureRows={}
for line in fixture.read_text().splitlines():
 if line.startswith('#'):continue
 c=line.split('\t');assert len(c)==7 and c[0] not in fixtureRows;fixtureRows[c[0]]=[c[1],c[2],*map(int,c[3:])]
assert fixtureRows==independent
for path,h in before_meta['unchangedGoldenResourceHashes'].items():assert sha(R/path)==h==sha(RUNS/cfg['compileSlot']/'resources'/path.split('/src/test/resources/')[1])
oldCases={(cls,n+'()') for path,cls in cfg['testClasses'].items() for n in re.findall(cfg['declarationRegex'],subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path],text=True))};newCases={(x['classname'],x['name']) for x in cases};added=newCases-oldCases;assert len(oldCases)==15 and oldCases<=newCases and len(added)==1;newKey=next(iter(added));assert newKey[1]=='anonymousRequestKeepsOptionalAuditMetadataAbsentOnTheWire()'
logPath=next(p for p in cfg['testClasses'] if p.endswith('/WebLogActionContractTest.java'));l=(R/logPath).read_text();a=l.index('  @Test // PT-PRO-QA054-013');b=l.index('  private static WebLogEventData legacy(',a);inverse=l[:a]+l[b:];inverse=inverse.replace('import static org.junit.jupiter.api.Assertions.assertTrue;\n','',1);inverse=inverse.replace('    var workers = Executors.newFixedThreadPool(2);\n    try {','    try (var workers = Executors.newFixedThreadPool(2)) {',1);inverse=inverse.replace('    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));\n    }','    }',1);assert inverse==subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+logPath],text=True)
anon=R/pf['anonymousExpectedVector']['path'];assert sha(anon)==pf['anonymousExpectedVector']['sha256'];w=anon.read_bytes();assert len(w)==2080 and w[974:2067]==b' '*1093 and w[17:33]==b'REQUEST         ' and w[2067:]==b' '*13
assert 'PayloadCodec.maximumForDigits(' not in (R/next(p for p in cfg['testClasses'] if p.endswith('/PayloadGoldenVectorTest.java'))).read_text()
inverse_rows=[dict(path=logPath,rawOriginalTwelveRestored=True),dict(path=next(p for p in cfg['testClasses'] if p.endswith('/PayloadGoldenVectorTest.java')),declaredOracleStrengthening=True,existingHashCorpusUnchanged=True)]

index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256'];physical=cfg['currentMainPhysical'];assert len(physical)==1 and physical==m['physical']==pf['physical']
normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json')
with zipfile.ZipFile(normal['jars']['protocol']['path']) as z:
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

O.mkdir();suite=E.Element('testsuite',name='PG24544_PROTOCOL_ORIGINAL15_NEW1',tests='16',failures='0',errors='0',skipped='0')
for x in cases:E.SubElement(suite,'testcase',classname=x['classname'],name=x['name'],time=x['seconds'])
E.ElementTree(suite).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
shutil.copyfile(anon,O/'anonymous-expected.wire')
shutil.copyfile(R/limitsRef['path'],O/'independent-limits-manifest.json')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],sourceMainUnchanged=True,tests=16,testClasses=2,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=15,newUniqueTests=1,sourcePrograms=1,physicalClasses=1,coverage=coverage,wholeTargetLmc100=True,naturalZeroBranchSourceNames=natural_zero,individualSourceCounters=individual,aggregateBranchRate=None,branchStatus='RECORD_NATURAL_BRANCH_ZERO_NO_ARTIFICIAL100',aggregateApplicableFour100=False,allSourcesNonemptyFour100=not bool(natural_zero),strictNonemptyFour100GateExit=1 if natural_zero else 0,oldLogTwelveRawRestorable=True,originalGoldenHashCorpusUnchanged=True,independentLimitsExpectedGuard=True,originalFutureGetBoundsSeconds=10,twoFixedPoolTerminationBoundsSeconds=10,rawExactInverseRows=inverse_rows,originalTestIdsPreserved=True,independentLayoutRows=64,repeatingLayouts=14,responseLayouts=31,newAnonymousCasePassed=True,original15Passed=True,anonymousExpectedVector=pf['anonymousExpectedVector'],anonymousByteEqualityAssertPassed=True,actualAnonymousRawRecorded=False,productionDerivedMaximumExpectedRemoved=True,productionNumericBoundaryInputRemoved=True,originalWaitBoundsSeconds=10,normalOwnerTerminationAsserted=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=12,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,manualCoverageExclusions=[],oldExecUnion=False,singleSession=cfg['session'],actualBackendOrRootVmNativeKeyOperations=False,noOriginalMethodExtractionOrSubstitute=True,reportedEnvironment=env,caseTimings=cases,originalXmlPins=pins,productTestsExecuted=16,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,globalYkt2177Accepted=False,bugs=['BUG-2541','BUG-2542'],ykts=['YKT-2177','YKT-2266'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=16,coverage=coverage,aggregateBranchRate=None,naturalZeroSources=natural_zero,strictSourceNonemptyFour100Gate=1 if natural_zero else 0,observedMain=len(positive),heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
