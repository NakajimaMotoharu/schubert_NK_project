"""Independent original-class/unchanged golden oracle/source/CRC proof; partial coverage retained."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22716-golden-three-unit-v1';S=RUNS/'pg22714-golden-three-static-v1';O=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG22722-golden-three-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 c=0
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^0xd800000000000000 if c&1 else c>>1
 return f'{c:016x}'
def main():
 assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,3,0,0,0)
 for n,h in {**b['inputHashes'],**b['mainInputs']}.items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
 for n,h in b['dependencies'].items():assert sha(n)==h
 for label,s in m['stages'].items():
  assert s['actualExit']==0 and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==s[stream+'Sha256']
 assert load(U/'unit-exit.safe.json')==m['stages']['unit'];cmd=m['stages']['unit']['command'];selected='dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest';assert cmd.count('--select-class')==1 and cmd[-1]==selected and '--select-method' not in cmd and '--scan-classpath' not in cmd
 original=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG22708-golden-wait-original-v1';orig=load(original/'manifest.json');old=original/'PayloadGoldenVectorTest.java';assert sha(old)==orig['sha256'];text=old.read_text()
 for a,z in [('start.await();','assertTrue(start.await(10, java.util.concurrent.TimeUnit.SECONDS));'),('ready.await();','assertTrue(ready.await(10, java.util.concurrent.TimeUnit.SECONDS));'),('future.get()','future.get(10, java.util.concurrent.TimeUnit.SECONDS)')]:assert text.count(a)==1;text=text.replace(a,z)
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_golden_token_guard',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);actual=(R/orig['path']).read_text();assert lm.java_tokens(text)==lm.java_tokens(actual)
 for bad in [actual.replace('start.await(10, java.util.concurrent.TimeUnit.SECONDS)','start.await()',1),actual.replace('future.get(10, java.util.concurrent.TimeUnit.SECONDS)','future.get()',1),actual.replace("expected[0] = 'A';","expected[0] = 'B';",1)]:assert lm.java_tokens(text)!=lm.java_tokens(bad)
 resource='src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv';assert sha(R/resource)==hashlib.sha256(subprocess.check_output(['git','show',orig['source']+':'+resource],cwd=R)).hexdigest();assert len([x for x in (R/resource).read_text().splitlines() if x and not x.startswith('#')])==64
 expected={(selected,n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(',old.read_text())};assert len(expected)==3;cases=[];environment={}
 for p in (U/'xml').glob('TEST-*.xml'):
  root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(t.get('classname'),t.get('name')) for t in root.findall('testcase')]
  environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
 assert set(cases)==expected and len(cases)==3
 for x in ['3 tests found','3 tests started','3 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert x in (U/'unit.stdout').read_text()
 normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);jar=Path(nm['jars']['protocol']['path']);assert sha(jar)==nm['jars']['protocol']['sha256'];physical={};ids={}
 with zipfile.ZipFile(jar) as z:
  for n in z.namelist():
   if n.startswith('dev/codex/schubert/nk/protocol/') and n.endswith('.class') and not n.endswith('package-info.class'):
    data=z.read(n);name=n[:-6];physical[name]=hashlib.sha256(data).hexdigest();ids[name]=crc64(data);assert sha(U/'component'/n)==physical[name]
 assert physical==m['physical'];assert {n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}==ids
 ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22716-GOLDEN-THREE"' in ex;probes={n:[c,int(hit),int(total)] for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
 for name,p in probes.items():
  if name.startswith('dev/codex/schubert/nk/') and not name.startswith(selected.replace('.','/')):assert name in ids and ids[name]==p[0]
 init={n for n in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(selected.replace('.','/'))};assert init and init<=set(ids)
 root=E.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in root.findall('.//class')}==set(ids);counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert counters['LINE']['covered']>0;coverage100=all(x['missed']==0 for x in counters.values())
 sm=load(S/'manifest.json');assert sm['inputHashes']==b['inputHashes'] and sm['mainInputs']==b['mainInputs'];assert not sm['reports']['checkstyle']['items'];assert all(not rep['processingErrors'] for rep in sm['reports'].values());findings=sm['reports']['pmd']['items'];assert len(findings)==2
 classified=[]
 for f in findings:
  assert f['rule']=='DoNotUseThreads' and f['method']=='sharedCodecProducesIdenticalBytesUnderConcurrentUse';assert (f['beginline'],f['endline']) in [('141','141'),('145','150')]
  classified.append(dict(finding=f,classification='NOT_APPLICABLE',reason='Standalone host PT owns fixed executor8 and workers inside try-with-resources; both latches and future have asserted finite10SECONDS. No J2EE/container/application thread creation. Site141 owns executor, site145-150 submits pure in-memory protocol operation.'))
 assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0
 cp=RUNS/'pg22712-golden-three-compile-v1/manifest.json';assert sha(cp)==b['compileManifestSha256'] and load(cp)['actualExit']==0 and load(cp)['inputHashes']==b['inputHashes']
 O.mkdir();files={}
 for base,prefix in [(U,'original-'),(S,'static-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file():
    name=prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=3,newUniqueTests=0,requalifiedExistingTests=3,newSourceProofs=0,newAcceptance=0,waitDeadlineAdditions=3,sourceTransformNegativeChecks=3,allOtherJavaTokensAndGoldenOracleUnchanged=True,resourceSha256=sha(R/resource),coverage=counters,wholeProtocolCoverage100=coverage100,coverageScope='This single whole original Test class only; unvisited module Code remains missed. Not a whole-module requalification and not additive to historical exec.',physical=physical,classIds=ids,rawProbes={n:probes[n] for n in ids if n in probes},productInitializations=sorted(init),backendRootNativeFourHeldActions=0,staticRaw=2,individualStaticClassifications=classified,staticApplicable=0,checkstyle=0,unchangedMainSpotbugs=sm['unchangedMainStaticSha256'],oldExecCombined=False,whole451Accepted=False,formalUpdated=False,effortRate=None,inputHashes=b['inputHashes'],environment=environment,files=files,bug='BUG-2447',yktStillOpen='YKT-2177',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
 (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requalified=3,newUnique=0,counters=counters,wholeProtocolCoverage100=coverage100,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
