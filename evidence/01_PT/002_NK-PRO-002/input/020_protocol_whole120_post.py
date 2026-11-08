"""Independent same-source complete Protocol evidence join; no runtime re-execution."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,xml.etree.ElementTree as E,zipfile,shutil,sys
R=Path.cwd();B=R/'evidence/01_PT/002_NK-PRO-002';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/017_protocol_whole120_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24642-protocol-whole120-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=load(U/'begin.json');assert m['begin']==begin
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,120,0,0,0) and begin['source']==sys.argv[1] and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert (begin['expectedTests'],begin['newMethods'],begin['requalifiedExistingMethods'])==(120,1,119)
for n,h in begin['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+n])).hexdigest()
for n,h in begin['dependencies'].items():assert sha(Path(n))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and stage['timedOut'] is False
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==24 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in part and 'sessionid='+cfg['session'] in part for part in cmd)
expected={(owner,n+'()') for path,owner in cfg['testClasses'].items() for n in re.findall(cfg['declarationRegex'],(R/path).read_text())};assert len(expected)==120
actual=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped'])
 for t in tree.findall('testcase'):actual.append(dict(classname=t.get('classname'),name=t.get('name'),seconds=t.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(actual)==120 and {(v['classname'],v['name']) for v in actual}==expected
summary=(U/'unit.stdout').read_text()
for s in ['120 tests found','120 tests started','120 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert s in summary
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes'] and pf['cases']=={owner:re.findall(cfg['declarationRegex'],(R/path).read_text()) for path,owner in cfg['testClasses'].items()}
assert (pf['expectedTests'],pf['testSources'],pf['physicalClasses'],pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'])==(120,25,176,17,0,0)
assert pf['compileManifestSha256']==begin['compileManifestSha256']==sha(RUNS/cfg['compileSlot']/'manifest.json') and pf['staticManifestSha256']==sha(RUNS/cfg['staticSlot']/'manifest.json')
normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');indexPath=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexPath)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';ix=load(indexPath);physical=cfg['currentMainPhysical'];assert m['physical']==physical and len(physical)==176
with zipfile.ZipFile(normal['jars']['protocol']['path']) as z:
 assert set(physical)=={n[:-6] for n in z.namelist() if n.endswith('.class')}
 for n,h in physical.items():assert sha(U/'component'/(n+'.class'))==hashlib.sha256(z.read(n+'.class')).hexdigest()==h==ix[n]['sha256']
info={n:crc for crc,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};annotationNames={n for n in physical if n.endswith('/package-info')};assert len(annotationNames)==7 and all(ix[n]['hasCode'] is False for n in annotationNames)
expectedInfo={n:ix[n]['crc64'] for n in physical if n not in annotationNames};assert len(expectedInfo)==169 and info==expectedInfo
for variant in [dict(list(expectedInfo.items())[1:]),dict(expectedInfo,unexpected='0'*16),dict(expectedInfo,**{next(iter(expectedInfo)):'0'*16}),{**expectedInfo,next(iter(annotationNames)):ix[next(iter(annotationNames))]['crc64']}]:assert variant!=expectedInfo
execText=(U/'execinfo.stdout').read_text();assert execText.count('Session "')==1 and 'Session "'+cfg['session']+'"' in execText
probes={n:[identity,int(hit),int(total)] for identity,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',execText,re.M)}
testPrefixes=[v.replace('.','/') for v in cfg['testClasses'].values()]+['dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle'];positive={n for n,v in probes.items() if v[1]>0 and n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testPrefixes)}
assert positive and positive<=set(physical) and all(probes[n][0]==ix[n]['crc64'] for n in positive)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(h in n for h in held for n in probes)
init=re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text());assert not any(h in n for h in held for n in init)
root=E.parse(U/'coverage.xml').getroot();counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(k in counters for k in ['LINE','METHOD','CLASS','BRANCH']);reportClasses={x.get('name'):x for x in root.findall('.//class')};assert set(reportClasses)<=set(physical)
noCode={n for n in physical if not ix[n]['hasCode']};assert len(noCode)==13 and len([n for n in noCode if n.endswith('package-info')])==7
notMeasuredCode=sorted(n for n in physical if n not in noCode and n not in reportClasses)
misses=[dict(className=n,counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in t.findall('counter')}) for n,t in reportClasses.items() if any(int(x.get('missed')) for x in t.findall('counter'))]
allFour=all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH'])
perSource=[]
for package in root.findall('package'):
 for src in package.findall('sourcefile'):
  perSource.append(dict(package=package.get('name'),name=src.get('name'),counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in src.findall('counter')}))
# Preserve every119 original method and both old oracle corpora; verify new caller assertion path.
assert pf['original119MethodsPreserved'] is True and pf['originalFieldSixRawRestored'] is True and pf['newIndependentCauseMethods']==1
oldset={(owner,n+'()') for path,owner in cfg['testClasses'].items() for n in re.findall(cfg['declarationRegex'],subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path],text=True))};assert len(oldset)==119 and oldset<=expected and expected-oldset=={('dev.codex.schubert.nk.protocol.codec.FieldCodecTest','malformedAndOverflowFailuresRetainDiagnosticCauseWithoutEchoingInput()')}
fieldPath='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecTest.java';raw=(R/fieldPath).read_text();a=raw.index('  @Test // PT-CODEC-EXC-001');z=raw.rfind('\n}');inverse=raw[:a-1]+raw[z+1:]
for line in ['import static org.junit.jupiter.api.Assertions.assertInstanceOf;\n','import static org.junit.jupiter.api.Assertions.assertNull;\n','import java.nio.charset.MalformedInputException;\n']:inverse=inverse.replace(line,'',1)
assert inverse.encode()==subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+fieldPath])
for path in cfg['resources']:assert sha(R/path)==hashlib.sha256(subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path])).hexdigest()
# Reuse exact current compiler-filter byte evidence, never repeat javap or old product tests.
filtersPath=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG24594-protocol-whole-denominator-v1/manifest.json';assert sha(filtersPath)=='9448c8cf89988f4d9a579ea10c433e8bad3e417c1df7709472648d1b29638dfe';filters=load(filtersPath);filtered={n for n,t in reportClasses.items() if ix[n]['hasCode'] and not t.findall('method')};assert filtered=={r['name'] for r in filters['compilerRows']} and len(filtered)==4 and len(reportClasses)==169 and counters['CLASS']['covered']==159 and counters['CLASS']['missed']==0
for row in filters['compilerRows']:assert row['sha256']==physical[row['name']] and row['syntheticSwitchMap'] is True and row['officialMeasuredMethods']==0
assert not notMeasuredCode and len([n for n in noCode if n.endswith('package-info')])==7
O.mkdir();safe=E.Element('testsuite',name='PG24640_PROTOCOL_WHOLE120',tests='120',failures='0',errors='0',skipped='0')
for v in actual:E.SubElement(safe,'testcase',classname=v['classname'],name=v['name'],time=v['seconds'])
E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for n in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/n,O/n)
for source,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(source,O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],wholeFixtures=24,testSources=25,tests=120,failures=0,errors=0,skipped=0,aborted=0,newUniqueTests=1,existingTestsRequalified=119,sourcePrograms=165,physicalInputClasses=176,noCodeClasses=sorted(noCode),officialClassinfoClasses=len(info),packageAnnotationsOmittedByOfficialClassinfo=7,classinfoNegativeVectors=4,officialXmlClassEntries=len(reportClasses),officialMeasuredClasses=counters['CLASS']['covered']+counters['CLASS']['missed'],officialNoMeasuredCodeClasses=notMeasuredCode,coverage=counters,measuredFour100=allFour,strictMeasuredFour100GateExit=0 if allFour else 1,unclassifiedOfficialFilterCount=len(notMeasuredCode),currentProgramAcceptance=False,naturalZeroBranchSourceCount=sum('BRANCH' not in x['counters'] for x in perSource),perSourceCounters=perSource,missedClassDetails=misses,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,original119MethodsPreserved=True,originalFieldSixRawRestored=True,newIndependentCauseCasePassed=True,compilerSyntheticNoMeasuredClasses=sorted(filtered),compilerFilterEvidence=dict(path=str(filtersPath.relative_to(R)),sha256=sha(filtersPath)),allOriginalFiveFixturesUnchanged=True,singleSession=cfg['session'],oldExecUnion=False,manualCoverageExclusions=[],fixtureExtraction=False,pmdRawFindings=17,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,productTestsExecuted=120,reportedEnvironment=env,originalXmlPins=pins,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=120,coverage=counters,officialNoMeasuredCodeClasses=notMeasuredCode,positiveMain=len(positive),measuredFour100=allFour,manifestSha256=sha(O/'manifest.json'))))
