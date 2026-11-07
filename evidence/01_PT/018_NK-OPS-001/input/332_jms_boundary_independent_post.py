"""Independent new factory8 whole-source Code proof, literal oracle/static/normal CRC/actual-init checks."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';PROGRAM=R/'evidence/01_PT/005_NK-MSG-001';RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg23072-jms-boundary-unit-v1';S=RUNS/'pg23086-jms-boundary-static-v3';PRE=RUNS/'pg23084-jms-boundary-compile-v3';META=RUNS/'pg23056-jms-factory-passive-v1';O=PROGRAM/'evidence/PG23074-jms-boundary-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());sp=importlib.util.spec_from_file_location('jms_factory_post_lexer',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens

def crc64(data):
 value=0
 for b in data:
  value^=b
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
def contains(source,part):
 a=tok(source);b=tok(part);return any(a[i:i+len(b)]==b for i in range(len(a)-len(b)+1))
def body(source,name):
 match=re.search(r'(?:@Test\s+void|private static byte\[\])\s+'+name+r'\s*\([^)]*\)(?:\s*throws Exception)?\s*\{',source);assert match,name
 start=match.start();cur=source.index('{',match.start());depth=1;i=cur+1
 while depth:
  if source[i]=='{':depth+=1
  elif source[i]=='}':depth-=1
  i+=1
 return source[cur+1:i-1]
def recipe(source):
 parts={
 'envelope005LogoutSuccessKeepsLiteralBodyAndProperties':['VERSION_PROPERTY, TEST_VERSION'],
 'logoutReply':['header(280, "LOGRSP01", "S", "S")','put(body, 24, RESPONSE);','put(body, 60, REQUEST_ID);','put(body, 96, "20261107210000000");','put(body, 113, "a".repeat(64));','put(body, 181, "000024");','put(body, 199, "000000280");','put(body, 208, "0000");','put(body, 256, "20261107210000000");'],
 'envelope006EmptyAndReservedHeaderNeverAcquireMessage':["reserved[212] = 'X';",'List.of(new byte[0], reserved)'],
 'envelope007InternalEventNeverAcquiresMessage':['header(320, "QWKREQ01", "E", "I")','put(event, 24, RESPONSE);','put(event, 60, REQUEST_ID);','put(event, 181, "000064");','put(event, 199, "000000320");','put(event, 256, "R".repeat(26));','put(event, 282, "000000000001");','put(event, 294, "000000000002");'],
 'envelope008ShortBodyAndExactCapMismatchNeverAcquireMessage':['new int[] {279, 1_000_000}','Arrays.copyOf(valid, length)']}
 return contains(source, 'private static final String TEST_VERSION = \"001\";') and all(all(contains(body(source,n),p) for p in ps) for n,ps in parts.items())
def original_inverse(source):
 value=tok(source)
 constant=tok('private static final String TEST_VERSION = "001";');index=next(i for i in range(len(value)) if value[i:i+len(constant)]==constant);del value[index:index+len(constant)]
 for name in ['envelope005LogoutSuccessKeepsLiteralBodyAndProperties','envelope006EmptyAndReservedHeaderNeverAcquireMessage','envelope007InternalEventNeverAcquiresMessage','envelope008ShortBodyAndExactCapMismatchNeverAcquireMessage','logoutReply']:
  start=next((i for i,v in enumerate(value) if v==name and i>0 and (value[i-1]=='void' or value[i-1]==']')),None);assert start is not None
  left=start-1
  if value[left]=='void':
   assert value[left-2:left]==['@','Test'];left-=2
   assert value[left-1].startswith('/** PT-JMS-ENV00');left-=1
  else:
   assert value[left-4:left+1]==['private','static','byte','[',']'];left-=4
  begin=next(i for i in range(start,len(value)) if value[i]=='{');depth=1;end=begin+1
  while depth:
   depth+= (value[end]=='{')-(value[end]=='}');end+=1
  del value[left:end]
 return ['"001"' if v=='TEST_VERSION' else v for v in value]
def main():
 assert not O.exists();cfg=load(B/'input/331_jms_boundary_scope.json');m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,8,0,0,0);target=cfg['targetPhysical'][0];assert target=='dev/codex/schubert/nk/api/messaging/outbound/JmsMessageFactory' and len(cfg['targetPhysical'])==1;assert b['selected']==list(cfg['testClasses'].values()) and len(b['selected'])==1
 for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
 assert subprocess.check_output(['git','diff','--name-only','7aed8eace7c844c2f79f2e39db766faf914890d5',b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()==''
 for p,h in b['dependencies'].items():assert sha(p)==h
 assert any(p.endswith('/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar') for p in b['dependencies']);assert not any(x in p.lower() for p in b['dependencies'] for x in ['artemis','postgresql','spring','bootstrap','schubert-nk-storage'])
 for label,stage in m['stages'].items():
  assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
 cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and cmd[cmd.index('--select-class')+1]==b['selected'][0] and '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in x for x in cmd);testpath=next(iter(cfg['testClasses']));source=(R/testpath).read_text();assert source.count('@Test')==8 and recipe(source);expected={(b['selected'][0],n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(',source)};assert len(expected)==8;assert not any(x in source for x in ['EmbeddedActiveMQ','ActiveMQConnectionFactory','DriverManager','Class.forName','System.getenv','Files.','ProcessBuilder','Executors.','FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException']);recipeNegative=[]
 original=PROGRAM/'evidence/PG23064-jms-original-four-freeze-v1/original-test.txt';assert original_inverse(source)==tok(original.read_text());assert not (R/testpath).with_name('JmsMessageFactoryPortTest.java').exists()
 historical=PROGRAM/'evidence/provisional/PG18602-jms-reply-envelope-unit-v1/manifest.json';hm=load(historical);assert hm['actualExit']==0 and hm['tests']==4 and hm['testInputHash']==sha(original)
 for a,z in [('private static final String TEST_VERSION = \"001\";', 'private static final String TEST_VERSION = \"002\";'),('reserved[212]', 'reserved[213]'),('put(event, 282, "000000000001");','put(event, 283, "000000000001");'),('put(body, 208, "0000");','put(body, 208, "0100");'),('new int[] {279, 1_000_000}','new int[] {281, 1_000_001}')]:
  assert a in source;assert not recipe(source.replace(a,z,1));recipeNegative.append(a)
 cases=[];environment={}
 for p in (U/'xml').glob('TEST-*.xml'):
  root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(v.get('classname'),v.get('name')) for v in root.findall('testcase')];environment.update({v.get('name'):v.get('value') for v in root.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
 assert len(cases)==8 and set(cases)==expected
 for text in ['8 tests found','8 tests started','8 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
 normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);normalBytes={};owners={}
 for module in ['protocol','api']:
  jar=Path(nm['jars'][module]['path']);assert sha(jar)==nm['jars'][module]['sha256']
  with zipfile.ZipFile(jar) as z:
   for n in z.namelist():
    if n.endswith('.class'):
     name=n[:-6];assert name not in normalBytes;normalBytes[name]=z.read(n);owners[name]=module
 assert not any(n.startswith(target+'$') for n in normalBytes);physical={target:hashlib.sha256(normalBytes[target]).hexdigest()};ids={target:crc64(normalBytes[target])};assert m['physical']==physical and sha(U/'component'/(target+'.class'))==physical[target];assert {n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}==ids;ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23072-JMS-BOUNDARY"' in ex;probes={n:[c,int(hit),int(total)] for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};prefix=b['selected'][0].replace('.','/');observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};assert {n for n in observed if n.startswith('dev/codex/schubert/nk/api/')}=={target}
 for n in observed:assert n in normalBytes and probes[n][0]==crc64(normalBytes[n]) and probes[n][1]>0
 init={n for n in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};physicalInit=init&set(normalBytes);generated=init-physicalInit;assert len(physicalInit)==14 and {n for n in physicalInit if n.startswith('dev/codex/schubert/nk/api/')}=={target}
 def lambda_owner(n):
  match=re.fullmatch(r'(dev/codex/schubert/nk/protocol/(?:codec/HeaderCodec|header/ResultCode))\$\$Lambda\+0x[0-9a-f]+',n);return match.group(1) if match else None
 assert len(generated)==4 and collections.Counter(lambda_owner(n) for n in generated)=={'dev/codex/schubert/nk/protocol/codec/HeaderCodec':2,'dev/codex/schubert/nk/protocol/header/ResultCode':2};assert not any(x in n for n in init for x in ['FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException']);assert all(n in observed for n in physicalInit)
 for n in ['dev/codex/schubert/nk/protocol/codec/Other$$Lambda+0x12','dev/codex/schubert/nk/protocol/codec/HeaderCodec$$Lambda+bad']:assert lambda_owner(n) is None
 meta=load(META/'manifest.json');assert meta['actualExit']==0 and meta['productTestsExecuted']==0 and all(meta['jars'][k]==nm['jars'][k] for k in ['protocol','api'])
 for stream in ['stdout','stderr']:assert sha(META/('javap.'+stream))==meta['stage'][stream+'Sha256']
 blocks=(META/'javap.stdout').read_text().split('Classfile ')[1:];assert len(blocks)==3
 for owner in set(map(lambda_owner,generated)):
  block=next(v for v in blocks if owner+'.class' in v.splitlines()[0]);assert 'java/lang/invoke/LambdaMetafactory.metafactory' in block and 'InvokeDynamic' in block
 codeblock=next(v for v in blocks if target+'.class' in v.splitlines()[0]);assert 'ACC_ENUM' in codeblock and 'createReply' in codeblock;root=E.parse(U/'coverage.xml').getroot();assert {v.get('name') for v in root.findall('.//class')}=={target};cs={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in root.findall('counter')};assert all(v['missed']==0 for v in cs.values()) and {k:cs[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=16,METHOD=2,CLASS=1,BRANCH=6)
 cp=load(PRE/'manifest.json');assert cp['actualExit']==0 and cp['inputHashes']==b['inputHashes'] and sha(PRE/'manifest.json')==b['compileManifestSha256'];assert {str(p.relative_to(PRE/'classes')):sha(p) for p in (PRE/'classes').rglob('*.class')}==cp['classHashes'];sm=load(S/'manifest.json');assert sm['inputHashes']==b['inputHashes'] and not sm['reports']['checkstyle']['items'] and all(not v['processingErrors'] for v in sm['reports'].values());assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0;findings=sm['reports']['pmd']['items'];assert collections.Counter(v['rule'] for v in findings)=={'UseConcurrentHashMap':1,'UseProperClassLoader':2};classifications=[]
 for f in findings:
  if f['rule']=='UseConcurrentHashMap':
   assert f['class']=='JmsReplyEnvelopeContractTest.Fixture' and f['variable']=='properties';reason='Private synchronous Fixture has no worker/callback publication. Exact property recorder is per invocation; normal whole8 runs with parallel disabled.'
  else:
   assert f['method']=='Fixture' and f['class']=='JmsReplyEnvelopeContractTest.Fixture';reason='Exact fixed JMSContext/BytesMessage interface defining loader supplies the local Proxy API visibility, no J2EE application resource/classloader lookup or provider. Actual whole8 succeeds in this classpath.'
  classifications.append(dict(finding=f,classification='NOT_APPLICABLE',reason=reason,testSourceSha256=sha(R/testpath)))
 goldp=PROGRAM/'evidence/PG23034-jms-factory-independent-input-v1/manifest.json';gold=load(goldp);assert gold['actualExit']==0 and gold['productionMethodsInvoked']==0 and gold['actualCredentialsOrSessions'] is False and {k:v['length'] for k,v in gold['vectors'].items()}=={'sync':280,'async':320,'request':256,'event':320}
 for ref in gold['designRefs']:assert hashlib.sha256(subprocess.check_output(['git','show',ref['commit']+':'+ref['path']],cwd=R)).hexdigest()==ref['sha256']
 O.mkdir();files={}
 for base,pref in [(U,'original-'),(S,'static-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file():
    name='jacoco.exec' if p.name=='jacoco.exec' else pref+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=8,newUniqueTests=4,requalifiedExistingTests=4,deletedDuplicateTestMethods=8,netUniqueTestsDelta=-4,newDirectWholeSourceProof=0,registeredWholeComponentDelta=0,registryDedupRequired=False,newAcceptance=0,coverage=cs,wholeTargetCodeCoverage100=True,physical=physical,classIds=ids,sourcePhysicalClosureCount=1,enumGeneratedMethods='Standard JaCoCo enum compiler-generated method filters only; whole normal physical class retained; manual excludes0',manualCoverageExclusions=[],oldExecCombined=False,normalObservedCrc={n:crc64(normalBytes[n]) for n in sorted(observed)},physicalProductInitializations=sorted(physicalInit),jvmGeneratedLambdaOwners={n:lambda_owner(n) for n in sorted(generated)},lambdaOwnerNegativeGuards=2,independentGoldenInput=dict(path=str(goldp.relative_to(R)),sha256=sha(goldp)),sourceRecipeNegativeGuards=recipeNegative,staticRaw=3,individualStaticClassifications=classifications,staticApplicable=0,checkstyle=0,unchangedMainStatic=sm['unchangedMainStaticSha256'],newFixtureReplacesHeldBackendTest=False,actualBrokerConnectionSessionTransactionSendCommitRollbackCloseRootNativeFourHeldActions=0,previousFourProof=dict(path=str(historical.relative_to(R)),sha256=sha(historical)),originalInverseTokensPreserved=True,bugs=['BUG-2471','BUG-2472'],ykts=['YKT-2209','YKT-2210'],inputHashes=b['inputHashes'],environment=environment,files=files,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newTests=4,coverage=cs,normalInit=14,generated=4,staticApplicable=0,registryDelta=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
