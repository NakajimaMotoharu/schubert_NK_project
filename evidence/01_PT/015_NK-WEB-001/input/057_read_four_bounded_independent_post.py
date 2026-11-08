"""Changed original whole32: independent exact edits/CRC/XML and natural-zero-branch accounting."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,xml.etree.ElementTree as E,shutil,zipfile
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/054_read_four_bounded_scope.json');U=RUNS/cfg['unitSlot'];O=B/'evidence/PG24326-read-four-bounded-thirtytwo-independent-v1';assert not O.exists();m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,32,0,0,0)
assert begin['source']=='99acc908a59b3a929814b42cc6777b9e51381d24' and begin['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert begin['expectedTests']==32 and begin['newMethods']==0 and begin['requalifiedExistingMethods']==32
for path,pin in begin['inputHashes'].items():assert sha(R/path)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for path,h in begin['dependencies'].items():assert sha(Path(path))==h
for label,stage in m['stages'].items():
 assert stage==load(U/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==4 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in cmd)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/path).read_text())};assert len(expected)==32
cases=[];pins={};env={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();pins[p.name]=sha(p);assert not any(tree.findall('.//'+t) for t in ['failure','error','skipped'])
 for x in tree.findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),seconds=x.get('time')))
 env.update({v.get('name'):v.get('value') for v in tree.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(cases)==32 and {(x['classname'],x['name']) for x in cases}==expected
for text in ['32 tests found','32 tests started','32 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['allOriginalOtherTokensAndOraclesPreserved'] and pf['noOriginalMethodExtractionOrSubstitute'] and pf['originalWholeMethods']==32
assert (pf['pmdRawFindings'],pf['applicableStaticViolations'],pf['checkstyleFindings'],pf['processingErrors'])==(26,0,0,0)
assert sha(RUNS/cfg['compileSlot']/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256'] and sha(RUNS/cfg['staticSlot']/'manifest.json')==pf['staticManifestSha256']
# Separate forward transformation from preflight's inverse; compare every remaining literal/token.
tok=lambda x:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',x))
for path in cfg['testClasses']:
 old=tok((R/cfg['beforeDirectory']/Path(path).name).read_text());new=tok((R/path).read_text());scenario=Path(path).name=='ScenarioWireClientTest.java'
 if not scenario:
  a='importjava.util.concurrent.Future;';assert old.count(a)==1;old=old.replace(a,a+'importjava.util.concurrent.TimeUnit;',1)
  a='for(varfuture:futures)future.get();';assert old.count(a)==1;old=old.replace(a,'for(varfuture:futures)future.get(10,TimeUnit.SECONDS);',1)
 a='try(varpool=Executors.newFixedThreadPool(8)){';assert old.count(a)==1;old=old.replace(a,'varpool=Executors.newFixedThreadPool(8);try{',1)
 a=('for(vartask:tasks)task.get(10,TimeUnit.SECONDS);}' if scenario else 'for(varfuture:futures)future.get(10,TimeUnit.SECONDS);}')
 assert old.count(a)==1;old=old.replace(a,a[:-1]+'}finally{pool.shutdownNow();assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}',1);assert old==new
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256'];physical=cfg['currentMainPhysical'];assert len(physical)==5 and physical==m['physical']==pf['physical']
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
for key,value in [('LINE',29),('METHOD',12),('CLASS',5)]:assert coverage[key]==dict(covered=value,missed=0)
def zero_branch_classinfo(text):
 rows=re.findall(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',text,re.M)
 assert len(rows)==len(physical)==5 and {v[6] for v in rows}==set(physical)
 assert all(int(v[1])==0 and v[5]==index[v[6]]['crc64'] for v in rows)
 return True
assert 'BRANCH' not in coverage and zero_branch_classinfo((U/'classinfo.stdout').read_text())
# Explicit standard XML zero omission, supported by actual class metadata, never interpreted as 100%.
coverage['BRANCH']=dict(covered=0,missed=0)
zero_branch_negative=[]
original_classinfo=(U/'classinfo.stdout').read_text();lines=original_classinfo.splitlines()
for label,altered in [('missingclass','\n'.join(lines[:-1])),('duplicateclass',original_classinfo+lines[-1]+'\n'),('nonzeroBranch',original_classinfo.replace('22      0','22      1',1)),('wrongclass',original_classinfo.replace('AnimationWireClient','AbsentWireClient',1))]:
 try:zero_branch_classinfo(altered)
 except AssertionError:zero_branch_negative.append(label)
 else:raise AssertionError('zero branch negative not rejected: '+label)

assert all(int(x.get('missed'))==0 for c in classes.values() for x in c.findall('counter'))
O.mkdir();suite=E.Element('testsuite',name='PG24324_READ_FOUR_WHOLE32',tests='32',failures='0',errors='0',skipped='0')
for x in cases:E.SubElement(suite,'testcase',classname=x['classname'],name=x['name'],time=x['seconds'])
E.ElementTree(suite).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(pfpath,'preflight-manifest.json'),(RUNS/cfg['compileSlot']/'manifest.json','compile-manifest.json'),(RUNS/cfg['staticSlot']/'manifest.json','static-manifest.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=begin['source'],productionCoreMain=begin['normalSource'],sourceMainUnchanged=True,tests=32,testClasses=4,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=32,newUniqueTests=0,sourcePrograms=4,physicalClasses=5,coverage=coverage,wholeTargetLmc100=True,naturalZeroBranchSources=4,branchRate=None,branchZeroXmlOmissionBoundToClassinfo=True,zeroBranchMetadataNegativeChecks=zero_branch_negative,branchStatus='NATURAL_ZERO_NOT_A_NONEMPTY_100_PERCENT',strictNonemptyFour100GateExit=1,allOriginalOtherTokensAndOraclesPreserved=True,independentForwardSourceRecipeVerified=True,threeFutureGetBoundsSeconds=10,fourFixedPoolTerminationBoundsSeconds=10,normalOwnerTerminationAsserted=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=26,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,manualCoverageExclusions=[],oldExecUnion=False,singleSession=cfg['session'],actualBackendOrRootVmNativeKeyOperations=False,noOriginalMethodExtractionOrSubstitute=True,reportedEnvironment=env,caseTimings=cases,originalXmlPins=pins,productTestsExecuted=32,newAcceptance=0,formalUpdated=False,effortRate=None,global451Accepted=False,globalYkt2177Accepted=False,bugs=['BUG-2526','BUG-2527'],ykts=['YKT-2177','YKT-2260'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=32,coverage=coverage,branchRate=None,strictFour100Gate=1,observedMain=len(positive),heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
