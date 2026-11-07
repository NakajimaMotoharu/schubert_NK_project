"""Whole original nine pure-memory cases: source/oracle, finite waits, CRC/session and actual graph."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22748-reply-nine-unit-v1';S=RUNS/'pg22746-reply-nine-static-v1';META=RUNS/'pg22752-reply-normal-passive-v1';O=R/'evidence/01_PT/005_NK-MSG-001/evidence/PG22750-reply-nine-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 c=0
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^0xd800000000000000 if c&1 else c>>1
 return f'{c:016x}'
def main():
 assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,9,0,0,0)
 cfg=load(R/'evidence/01_PT/018_NK-OPS-001/input/249_reply_wait_scope.json');targets=set(cfg['targetPhysical']);assert len(targets)==2
 for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
 for n,h in b['dependencies'].items():assert sha(n)==h
 for label,s in m['stages'].items():
  assert s['actualExit']==0 and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==s[stream+'Sha256']
 assert load(U/'unit-exit.safe.json')==m['stages']['unit'];cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and [cmd[i+1] for i,x in enumerate(cmd) if x=='--select-class']==b['selected']==list(cfg['testClasses'].values());assert '--select-method' not in cmd and '--scan-classpath' not in cmd
 original=R/cfg['original'];orig=load(original);expected=set();negative=0;transforms=0
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_reply_token_guard',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm)
 for item in orig['tests']:
  old=original.parent/(Path(item['path']).name);assert sha(old)==item['sha256'];text=old.read_text();assert text.count('start.await();')==item['waitSites'];transforms+=item['waitSites'];want=text.replace('start.await();','assertTrue(start.await(5, TimeUnit.SECONDS));');actual=(R/item['path']).read_text();assert lm.java_tokens(want)==lm.java_tokens(actual)
  for bad in [actual.replace('start.await(5, TimeUnit.SECONDS)','start.await()',1),actual.replace('DEADLINE = NOW.plusSeconds(2)','DEADLINE = NOW.plusSeconds(3)',1)]:assert lm.java_tokens(want)!=lm.java_tokens(bad);negative+=1
  expected|={(item['className'],name+'()') for name in re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)}
 assert transforms==5 and len(expected)==9;cases=[];environment={}
 for p in (U/'xml').glob('TEST-*.xml'):
  root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(t.get('classname'),t.get('name')) for t in root.findall('testcase')];environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
 assert set(cases)==expected and len(cases)==9
 for x in ['9 tests found','9 tests started','9 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert x in (U/'unit.stdout').read_text()
 normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);jar=Path(nm['jars']['web']['path']);assert sha(jar)==nm['jars']['web']['sha256'];physical={};ids={}
 with zipfile.ZipFile(jar) as z:
  for name in targets:
   data=z.read(name+'.class');physical[name]=hashlib.sha256(data).hexdigest();ids[name]=crc64(data);assert sha(U/'component'/(name+'.class'))==physical[name]
  assert not any(n.endswith('.class') and any(n.startswith(t+'$') for t in targets) for n in z.namelist())
 assert physical==m['physical'];assert {n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}==ids
 ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22748-REPLY-NINE"' in ex;probes={n:[c,int(hit),int(total)] for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
 for name in targets:assert probes[name][0]==ids[name] and probes[name][1]>0
 testprefixes=[n.replace('.','/') for n in b['selected']]
 for name in probes:
  if name.startswith('dev/codex/schubert/nk/') and not any(name.startswith(t) for t in testprefixes):assert name in targets
 init={n for n in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n.startswith(t) for t in testprefixes)}
 def lambda_owner(name):
  match=re.fullmatch(r'(dev/codex/schubert/nk/web/messaging/(?:ReplyCorrelationRegistry|PendingReply))\$\$Lambda\+0x[0-9a-f]+',name)
  return match.group(1) if match else None
 generated=init-targets;assert init-generated==targets and len(generated)==2 and {lambda_owner(n) for n in generated}==targets
 for bad in ['dev/codex/schubert/nk/web/messaging/Other$$Lambda+0x123','dev/codex/schubert/nk/web/messaging/PendingReply$$Lambda+nohex']:assert lambda_owner(bad) is None
 meta=load(META/'manifest.json');assert meta['actualExit']==0 and meta['productTestsExecuted']==0 and meta['normalWebJarSha256']==sha(jar)
 for stream in ['stdout','stderr']:assert sha(META/('javap.'+stream))==meta['stage'][stream+'Sha256']
 blocks=(META/'javap.stdout').read_text().split('Classfile ')[1:];assert len(blocks)==2
 for name in targets:
  block=next(x for x in blocks if name+'.class' in x.splitlines()[0]);assert 'java/lang/invoke/LambdaMetafactory.metafactory' in block and 'InvokeDynamic' in block
 root=E.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in root.findall('.//class')}==targets;cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert cs['LINE']['covered']>0;all100=all(v['missed']==0 for v in cs.values());family={x.get('name'):{v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in x.findall('counter')} for x in root.findall('.//class')}
 sm=load(S/'manifest.json');assert sm['inputHashes']==b['inputHashes'] and not sm['reports']['checkstyle']['items'] and all(not v['processingErrors'] for v in sm['reports'].values());findings=sm['reports']['pmd']['items'];assert len(findings)==8
 expectedSites={('ReplyCorrelationRegistryTest','oneOfOneHundredSimultaneousResponsesWins','107','107'),('ReplyCorrelationRegistryTest','oneOfOneHundredSimultaneousResponsesWins','111','118'),('ReplyCorrelationTerminalRaceTest','terminalRaceHasOneWinnerAndReturnsThePermit','36','36'),('ReplyCorrelationTerminalRaceTest','terminalRaceHasOneWinnerAndReturnsThePermit','44','48'),('ReplyCorrelationTerminalRaceTest','terminalRaceHasOneWinnerAndReturnsThePermit','50','54'),('ReplyCorrelationTerminalRaceTest','terminalRaceHasOneWinnerAndReturnsThePermit','56','60'),('ReplyCorrelationTerminalRaceTest','concurrentRegistrationsRespectCapacityAndReuseAllSlots','98','98'),('ReplyCorrelationTerminalRaceTest','concurrentRegistrationsRespectCapacityAndReuseAllSlots','103','107')};assert {(f['class'],f['method'],f['beginline'],f['endline']) for f in findings}==expectedSites
 classifications=[]
 for f in findings:
  assert f['rule']=='DoNotUseThreads';classifications.append(dict(finding=f,classification='NOT_APPLICABLE',reason='Standalone PT owns bounded executor (Registry16/terminal3/registration20) and submits only in-memory Registry actions. Each start latch asserts five-second deadline, caller Future already5/10SECONDS; try-with-resources joins workers. Not container/application thread creation. Exact owner/site retained.'))
 assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0
 cp=RUNS/'pg22744-reply-nine-compile-v1/manifest.json';assert sha(cp)==b['compileManifestSha256'] and load(cp)['actualExit']==0 and load(cp)['inputHashes']==b['inputHashes']
 O.mkdir();files={}
 for base,prefix in [(U,'original-'),(S,'static-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file():
    name='jacoco.exec' if p.name=='jacoco.exec' else prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=9,newUniqueTests=0,requalifiedExistingTests=9,newSourceProofs=0,newAcceptance=0,waitDeadlineAdditions=5,sourceTransformNegativeChecks=negative,allOtherJavaTokensFixturesAndOracleUnchanged=True,coverage=cs,familyCoverage=family,wholeTargetCodeCoverage100=all100,physical=physical,classIds=ids,rawProbes={n:probes[n] for n in targets},physicalProductInitializations=sorted(init-generated),jvmGeneratedLambdaOwners={n:lambda_owner(n) for n in sorted(generated)},lambdaOwnerNegativeGuards=2,backendRootNativeFourHeldActions=0,staticRaw=8,individualStaticClassifications=classifications,staticApplicable=0,checkstyle=0,unchangedMainSpotbugs=sm['unchangedMainStaticSha256'],oldExecCombined=False,whole451Accepted=False,formalUpdated=False,effortRate=None,inputHashes=b['inputHashes'],environment=environment,files=files,bug='BUG-2449',yktStillOpen='YKT-2177',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requalified=9,newUnique=0,counters=cs,wholeTargetCodeCoverage100=all100,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
