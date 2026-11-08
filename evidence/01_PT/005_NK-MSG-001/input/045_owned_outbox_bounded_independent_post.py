"""Original six independent post: preserve real PASS cases and nonzero target coverage gate."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path.cwd();B=R/'evidence/01_PT/005_NK-MSG-001';RUNS=R.parent/'pgpt-runs/PG379'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(B/'input/042_owned_outbox_bounded_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24262-owned-outbox-six-independent-partial-v1';assert not O.exists()
m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,6,0,0,0)
assert begin['source']=='0dde9bec886a5a7b535e5d9587d54dae2b8cc9a3' and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for path,pin in begin['inputHashes'].items():
 assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,pin in begin['dependencies'].items():assert sha(Path(path))==pin
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/path).read_text())}
assert len(expected)==6
cases=[];xmlpins={};environment={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 xmlpins[p.name]=sha(p);tree=E.parse(p).getroot();assert not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped'])
 for c in tree.findall('testcase'):cases.append(dict(classname=c.get('classname'),name=c.get('name'),seconds=c.get('time')))
 environment.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==6 and {(c['classname'],c['name']) for c in cases}==expected
for text in ['6 tests found','6 tests started','6 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['allOriginalTestOtherTokensAndOraclesPreserved'] and pf['heldAttachSecondaryUnreachable'] and pf['allSqlCallbacksNonReturning']
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(18,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256']
assert sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Independently reverse only the declared edits, and compare every remaining original token.
tok=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s))
path=next(iter(cfg['testClasses']));new=tok((R/path).read_text());old=tok((R/cfg['before']).read_text())
for n in ['release','gate']:
 a='assertTrue('+n+'.await(5,TimeUnit.SECONDS));';assert new.count(a)==1;new=new.replace(a,n+'.await();',1)
a='try(varexecutor=Executors.newSingleThreadExecutor()){try{';b='}finally{release.countDown();}}finally{release.countDown();owned.close();}'
assert new.count(a)==new.count(b)==1;new=new.replace(a,a[:-4],1).replace(b,'}finally{release.countDown();owned.close();}',1)
assert new==old
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256']
physical=cfg['currentMainPhysical'];assert physical==m['physical']==pf['physical'] and len(physical)==1
normal=load(RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json')
with zipfile.ZipFile(normal['jars']['api']['path']) as z:
 for n,pin in physical.items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==sha(U/'component'/(n+'.class'))==pin==index[n]['sha256']
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+cfg['session']+'"' in ex
probes={n:[identity,int(hits),int(total)] for identity,hits,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
tests=list(cfg['testClasses'].values());prefix=[v.replace('.','/') for v in tests]
positive={n for n,v in probes.items() if v[1]>0 and n.startswith('dev/codex/schubert/nk/') and not any(n==p or n.startswith(p+'$') for p in prefix)}
assert set(physical)<=positive and all(n in index and probes[n][0]==index[n]['crc64'] for n in positive)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
assert not any(n.split('/')[-1].split('$')[0] in held for n in positive)
initialized=re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text());assert not any(name in n for name in held for n in initialized)
tree=E.parse(U/'coverage.xml').getroot();classes={c.get('name'):c for c in tree.findall('.//class')};assert set(classes)==set(physical)
coverage={c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in tree.findall('counter')}
assert {k:coverage[k] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=dict(covered=65,missed=1),METHOD=dict(covered=9,missed=0),CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=28,missed=0))
assert coverage['INSTRUCTION']==dict(covered=239,missed=8)
methods={(v.get('name'),v.get('desc')) for c in classes.values() for v in c.findall('method')}
assert methods=={(v['name'],v['descriptor']) for v in cfg['expectedCodeMethods']}
missing=[dict(c.attrib) for c in tree.findall('.//sourcefile/line') if int(c.get('mi'))>0]
assert any(v['nr']=='76' and v['ci']=='0' for v in missing)
collateral=B/'evidence/PG24266-owned-outbox-collateral-counters-v1/manifest.json';co=load(collateral)
assert co['actualExit']==0 and co['unitExecSha256']==sha(U/'jacoco.exec') and co['repositoryAndSenderMeasuredConstructorOnly'] and co['retainFailureNotMeasured']
O.mkdir();safe=E.Element('testsuite',name='PG24260_OWNED_ORIGINAL_SIX',tests='6',failures='0',errors='0',skipped='0')
for row in cases:E.SubElement(safe,'testcase',classname=row['classname'],name=row['name'],time=row['seconds'])
E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(U/'begin.json','begin.safe.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
value=dict(actualExit=1,auditActualExit=0,targetCoverageGateExit=1,atJST=datetime.datetime.now().astimezone().isoformat(),branch='dev-foundation',source=begin['source'],productionCoreMain=begin['normalSource'],originalUnitExit=0,tests=6,testsPassed=6,testClasses=1,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=0,coverageQualifiedTests=0,newUniqueTests=0,coverage=coverage,wholeTargetApplicableCoverage100=False,missingInstructions=missing,physical=physical,allOriginalOtherTokensAndOraclesPreserved=True,independentReverseRecipeVerified=True,observedPositiveMainClasses=len(positive),allObservedMainCrcMatchCurrentNormal=True,heldFourPositiveMainProbes=0,heldFourInitializations=0,noNewFixtureOrMethodExtraction=True,noActualExternalBackendOperations=True,oldExecUnion=False,singleSession=cfg['session'],pmdRawFindings=18,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,caseTimings=cases,reportedEnvironment=environment,originalXmlPins=xmlpins,collateralCounterManifest=dict(path=str(collateral.relative_to(R)),sha256=sha(collateral)),productTestsExecuted=6,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,bugs=['BUG-2523','BUG-2524'],ykts=['YKT-2177','YKT-2258'],status='ORIGINAL_SIX_PASS_TARGET_SOURCE_COVERAGE_NOT_ACCEPTED',files={p.name:sha(p) for p in O.iterdir()},verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=1,auditActualExit=0,testsPassed=6,coverage=coverage,manifestSha256=sha(O/'manifest.json'))))
raise SystemExit(1)
