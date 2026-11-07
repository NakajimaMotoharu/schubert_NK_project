"""Original pure26: independent oracles, five wait edits, exact source/CRC/session and noCode ports."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22968-pure-resource-unit-v1';S=RUNS/'pg22966-pure-resource-static-v1';PRE=RUNS/'pg22964-pure-resource-compile-v1';META=RUNS/'pg22972-pure-resource-passive-v1';O=B/'evidence/PG22970-pure-resource-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 c=0
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^0xd800000000000000 if c&1 else c>>1
 return f'{c:016x}'
def main():
 assert not O.exists();m=load(U/'manifest.json');b=m['begin'];cfg=load(B/'input/303_pure_resource_scope.json');assert load(U/'begin.json')==b and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,26,0,0,0);targets=set(cfg['targetPhysical']);ports=set(cfg['noCodePorts']);assert targets=={'dev/codex/schubert/nk/storage/ResourceScope'} and len(ports)==4
 for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
 for n,h in b['dependencies'].items():assert sha(n)==h
 for label,stage in m['stages'].items():
  assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
 cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and [cmd[i+1] for i,x in enumerate(cmd) if x=='--select-class']==b['selected']==list(cfg['testClasses'].values());assert '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in x for x in cmd)
 original=R/cfg['original'];orig=load(original);lex=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('pure_resource_inverse_tokens',lex);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);tok=lm.java_tokens;expected=set();negative=0;waits=0
 for item in orig['tests']:
  old=R/item['snapshotPath'];assert sha(old)==item['sha256'];text=old.read_text();actual=(R/item['path']).read_text();restored=actual
  if Path(item['path']).name=='FactoryResourceScopeTest.java':
   assert actual.count('first.get(10, TimeUnit.SECONDS)')==actual.count('second.get(10, TimeUnit.SECONDS)')==2;restored=restored.replace('first.get(10, TimeUnit.SECONDS)','first.get()').replace('second.get(10, TimeUnit.SECONDS)','second.get()');waits+=4
  else:
   assert actual.count('futures.get(i).get(10, TimeUnit.SECONDS)')==1;restored=restored.replace('futures.get(i).get(10, TimeUnit.SECONDS)','futures.get(i).get()').replace('import java.util.concurrent.TimeUnit;','');waits+=1
  assert tok(restored)==tok(text);assert not any(v in actual for v in ['Files.','FileChannel','Linux','ProcessBuilder','Runtime.getRuntime','Class.forName','nativeLinker','System.getenv'])
  for a,z in [('10, TimeUnit.SECONDS','0, TimeUnit.SECONDS'),('10, TimeUnit.SECONDS','10, TimeUnit.MINUTES')]:assert tok(actual.replace(a,z,1))!=tok(actual);negative+=1
  expected|={(item['className'],name+'()') for name in re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)}
 assert waits==5 and len(expected)==26;cases=[];environment={}
 for p in (U/'xml').glob('TEST-*.xml'):
  root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(t.get('classname'),t.get('name')) for t in root.findall('testcase')];environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
 assert len(cases)==26 and set(cases)==expected
 for x in ['26 tests found','26 tests started','26 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert x in (U/'unit.stdout').read_text()
 normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);jar=Path(nm['jars']['storage']['path']);assert sha(jar)==nm['jars']['storage']['sha256'];normalNames=targets|{'dev/codex/schubert/nk/storage/StorageIoException','dev/codex/schubert/nk/storage/StorageIoException$Reason'};physical={};ids={};metadata={}
 with zipfile.ZipFile(jar) as z:
  assert {n[:-6] for n in z.namelist() if n.startswith('dev/codex/schubert/nk/storage/ResourceScope$') and n.endswith('.class')}==ports
  for name in normalNames|ports:
   data=z.read(name+'.class');ids[name]=crc64(data)
   if name in targets:physical[name]=hashlib.sha256(data).hexdigest();assert sha(U/'component'/(name+'.class'))==physical[name]
   if name in ports:metadata[name]=hashlib.sha256(data).hexdigest()
 assert physical==m['physical'];assert {n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}=={n:ids[n] for n in targets};ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22968-PURE-RESOURCE"' in ex;probes={n:[c,int(hit),int(total)] for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};prefixes=[n.replace('.','/') for n in b['selected']]
 observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not any(n.startswith(t) for t in prefixes)};assert observed==normalNames
 for n in observed:assert probes[n][0]==ids[n] and probes[n][1]>0
 assert not ports&set(probes);init={n for n in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n.startswith(t) for t in prefixes)}
 def lambda_owner(name):
  match=re.fullmatch(r'(dev/codex/schubert/nk/storage/ResourceScope)\$\$Lambda\+0x[0-9a-f]+',name);return match.group(1) if match else None
 generated=init-normalNames;assert init-generated==normalNames and len(generated)==2 and {lambda_owner(n) for n in generated}==targets
 for n in ['dev/codex/schubert/nk/storage/Other$$Lambda+0x123','dev/codex/schubert/nk/storage/ResourceScope$$Lambda+nothex']:assert lambda_owner(n) is None
 meta=load(META/'manifest.json');assert meta['actualExit']==0 and meta['productTestsExecuted']==0 and meta['normalStorageJarSha256']==sha(jar)
 for stream in ['stdout','stderr']:assert sha(META/('javap.'+stream))==meta['stage'][stream+'Sha256']
 blocks=(META/'javap.stdout').read_text().split('Classfile ')[1:];assert len(blocks)==7
 for name in ports:
  block=next(v for v in blocks if name+'.class' in v.splitlines()[0]);assert 'ACC_INTERFACE, ACC_ABSTRACT' in block and 'Code:' not in block and 'ACC_PUBLIC, ACC_ABSTRACT' in block
 codeblock=next(v for v in blocks if 'storage/ResourceScope.class' in v.splitlines()[0]);assert 'java/lang/invoke/LambdaMetafactory.metafactory' in codeblock and 'InvokeDynamic' in codeblock
 root=E.parse(U/'coverage.xml').getroot();assert {v.get('name') for v in root.findall('.//class')}==targets;cs={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in root.findall('counter')};assert all(v['missed']==0 for v in cs.values());assert {k:cs[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=52,METHOD=5,CLASS=1,BRANCH=20)
 cp=load(PRE/'manifest.json');assert cp['actualExit']==0 and cp['inputHashes']==b['inputHashes'] and sha(PRE/'manifest.json')==b['compileManifestSha256'];assert {str(p.relative_to(PRE/'classes')):sha(p) for p in (PRE/'classes').rglob('*.class')}==cp['classHashes'];sm=load(S/'manifest.json');assert sm['inputHashes']==b['inputHashes'] and not sm['reports']['checkstyle']['items'] and all(not v['processingErrors'] for v in sm['reports'].values());assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0;findings=sm['reports']['pmd']['items'];assert len(findings)==9
 oldscope=orig['currentStorage29'];hashes={n:sha(R/n) for n in oldscope['currentInputHashes']};changed=set(cfg['testClasses']);assert len(hashes)==29 and {n for n,h in hashes.items() if h!=oldscope['currentInputHashes'][n]}==changed;oldraw=oldscope['allCurrentRaw'];oldsites=[v for v in oldraw if v['path'] in changed];assert len(oldsites)==9;newsites=[];classified=[]
 for f in findings:
  matches=[n for n in changed if Path(n).stem==f['class']];assert len(matches)==1 and f['rule']=='DoNotUseThreads';row=dict(path=matches[0],**f);newsites.append(row);category='LOCAL_TOKEN_FACTORY_OWNERSHIP_PARALLEL_REGRESSION' if f['class']=='FactoryResourceScopeTest' else 'LOCAL_CLOSEABLE_CALLBACK_PARALLEL_INDEPENDENCE';classified.append(dict(finding=row,classification='NOT_APPLICABLE',category=category,reason='Standalone original JUnit pure ownership regression, not a J2EE application/container thread. Method-specific executor TWR owns all local tasks; each actual Future get now10SECONDS, existing factory latch10SECONDS preserves interrupt and asserts its deadline. Actions use separate local Token/Harness or independent result values, not native/FD/backend. Actual whole26 termination/normal graph verified on this source; this is not a blanket Test exemption or native completion claim.',currentSourceSha256=hashes[matches[0]],runtimeValidated=True))
 key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert collections.Counter(map(key,oldsites))==collections.Counter(map(key,newsites));current=[v for v in oldraw if v['path'] not in changed]+newsites;assert len(current)==82;assert len(oldscope['reviewedFindings'])==25 and not any(v['finding']['path'] in changed for v in oldscope['reviewedFindings']);assert len(classified)==9;O.mkdir();files={}
 for base,prefix in [(U,'original-'),(S,'static-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file():
    name='jacoco.exec' if p.name=='jacoco.exec' else prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=26,newUniqueTests=0,requalifiedExistingTests=26,newSourceProofs=0,newAcceptance=0,finiteWaitCorrections=5,sourceTransformNegatives=negative,allOtherJavaTokensFixturesAndOraclesUnchanged=True,coverage=cs,wholeTargetCodeCoverage100=True,physical=physical,noCodePorts=metadata,noCodePortCount=4,wholeSourcePhysicalClosure=5,noCodePortsCountersFabricated=False,normalObservedCrc={n:ids[n] for n in observed},physicalProductInitializations=sorted(normalNames),jvmGeneratedLambdaOwners={n:lambda_owner(n) for n in generated},lambdaOwnerNegativeGuards=2,backendRootNativeFourHeldActions=0,currentStorage29=dict(checkedSources=29,unchangedSources=27,changedSources=2,currentInputHashes=hashes,allCurrentRaw=current,reviewedFindings=oldscope['reviewedFindings']+classified,currentComposedRaw=82,individuallyClassified=34,applicableOnReviewedSubset=0,totalApplicableFindings=None,unclassified=48,freshAll29EngineRun=False),staticRaw=9,individualStaticClassifications=classified,staticApplicable=0,checkstyle=0,unchangedMainStatic=sm['unchangedMainStaticSha256'],oldExecCombined=False,whole451Accepted=False,formalUpdated=False,effortRate=None,inputHashes=b['inputHashes'],environment=environment,files=files,bug='BUG-2464',ykt='YKT-2202',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requalified=26,newUnique=0,counters=cs,noCodePorts=4,storageClassified=34,storageUnknown=48,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
