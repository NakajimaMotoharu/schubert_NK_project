"""Independent QA054 whole12, exact source transformation, current static25 binding and normal provenance."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22784-qa054-twelve-unit-v1';S=RUNS/'pg22782-qa054-twelve-static-v1';META=RUNS/'pg22786-qa054-normal-passive-v1';O=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG22788-qa054-twelve-independent-v1';TARGET='dev/codex/schubert/nk/protocol/layout/log/WebLogEventData'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def crc64(data):
 c=0
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^0xd800000000000000 if c&1 else c>>1
 return f'{c:016x}'
def main():
 assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert b==load(U/'begin.json') and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,12,0,0,0)
 for n,h in {**b['inputHashes'],**b['mainInputs']}.items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
 for n,h in {**b['dependencies'],**b['jacocoToolHashes']}.items():assert sha(n)==h
 for label,s in m['stages'].items():
  assert s['actualExit']==0 and not s['timedOut']
  for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==s[stream+'Sha256']
 assert load(U/'unit-exit.safe.json')==m['stages']['unit'];cmd=m['stages']['unit']['command'];selected='dev.codex.schubert.nk.protocol.layout.WebLogActionContractTest';assert cmd.count('--select-class')==1 and cmd[-1]==selected and '--select-method' not in cmd and '--scan-classpath' not in cmd
 op=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG22772-qa054-future-original-v1';original=load(op/'manifest.json');old=op/'WebLogActionContractTest.java';assert sha(old)==original['sha256'];text=old.read_text()
 for name in ['first','second']:assert text.count(name+'.get()')==1;text=text.replace(name+'.get()',name+'.get(10, java.util.concurrent.TimeUnit.SECONDS)')
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_qa054_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);actual=(R/original['path']).read_text();assert lm.java_tokens(text)==lm.java_tokens(actual)
 for bad in [actual.replace('first.get(10, java.util.concurrent.TimeUnit.SECONDS)','first.get()',1),actual.replace('second.get(10, java.util.concurrent.TimeUnit.SECONDS)','second.get()',1),actual.replace('put(data, 18, type);','put(data, 19, type);',1)]:assert lm.java_tokens(text)!=lm.java_tokens(bad)
 expected={(selected,n+'()') for n in re.findall(r'@Test[^\n]*\s+void\s+(\w+)\s*\(',old.read_text())};assert len(expected)==12;cases=[];environment={}
 for p in (U/'xml').glob('TEST-*.xml'):
  root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(x.get('classname'),x.get('name')) for x in root.findall('testcase')];environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
 assert len(cases)==len(set(cases))==12 and set(cases)==expected
 for v in ['12 tests found','12 tests started','12 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert v in (U/'unit.stdout').read_text()
 normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);jar=Path(nm['jars']['protocol']['path']);assert sha(jar)==nm['jars']['protocol']['sha256'];allids={};allhashes={}
 with zipfile.ZipFile(jar) as z:
  for name in z.namelist():
   if name.startswith('dev/codex/schubert/nk/protocol/') and name.endswith('.class'):
    data=z.read(name);allids[name[:-6]]=crc64(data);allhashes[name[:-6]]=hashlib.sha256(data).hexdigest()
  assert not any(name.startswith(TARGET+'$') for name in z.namelist())
 assert m['physical']=={TARGET:allhashes[TARGET]} and sha(U/'component'/(TARGET+'.class'))==allhashes[TARGET];assert {name:c for c,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}=={TARGET:allids[TARGET]}
 ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22784-QA054-TWELVE"' in ex;probes={n:[c,int(hit),int(total)] for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
 for n,v in probes.items():
  if n.startswith('dev/codex/schubert/nk/') and not n.startswith(selected.replace('.','/')):assert n in allids and v[0]==allids[n]
 init={n for n in re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(selected.replace('.','/'))};generated=init-set(allids);normalInit=init-generated;assert normalInit and normalInit<=set(allids)
 owners={'dev/codex/schubert/nk/protocol/'+s for s in ['codec/PayloadCodec','layout/LayoutFieldCatalog','layout/PayloadSemanticValidator','layout/PayloadTypeCatalog','layout/TypedFieldValues']}
 def lambda_owner(name):
  match=re.fullmatch(r'(dev/codex/schubert/nk/protocol/[A-Za-z0-9_/$]+)\$\$Lambda\+0x[0-9a-f]+',name)
  return match.group(1) if match and match.group(1) in owners else None
 assert generated and {lambda_owner(n) for n in generated}==owners
 for bad in ['dev/codex/schubert/nk/api/TemporaryInfrastructureException$$Lambda+0x123','dev/codex/schubert/nk/protocol/layout/Unknown$$Lambda+0x123','dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$$Lambda+nothex']:assert lambda_owner(bad) is None
 meta=load(META/'manifest.json');assert meta['actualExit']==0 and meta['productTestsExecuted']==0 and meta['normalProtocolJarSha256']==sha(jar)
 for stream in ['stdout','stderr']:assert sha(META/('javap.'+stream))==meta['stage'][stream+'Sha256']
 blocks=(META/'javap.stdout').read_text().split('Classfile ')[1:];assert len(blocks)==6
 for name in owners:
  block=next(v for v in blocks if name+'.class' in v.splitlines()[0]);assert 'java/lang/invoke/LambdaMetafactory.metafactory' in block and 'InvokeDynamic' in block
 targetmeta=next(v for v in blocks if TARGET+'.class' in v.splitlines()[0]);assert 'java/lang/runtime/ObjectMethods.bootstrap' in targetmeta and 'WebLogEventData[REDACTED]' in targetmeta
 root=E.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in root.findall('.//class')}=={TARGET};cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(v['missed']==0 for v in cs.values()) and {k:cs[k]['covered'] for k in ['LINE','METHOD','CLASS']}==dict(LINE=50,METHOD=5,CLASS=1);assert 'BRANCH' not in cs;methods={v.get('name') for v in root.findall('.//class/method')};assert methods=={'<init>','from','fields','toString'}
 sm=load(S/'manifest.json');assert sm['inputHashes']==b['inputHashes'] and all(not v['processingErrors'] for v in sm['reports'].values()) and not sm['reports']['checkstyle']['items'];findings=sm['reports']['pmd']['items'];assert len(findings)==4 and {(v['rule'],v['beginline'],v['endline']) for v in findings}=={('NullAssignment','179','179'),('DoNotUseThreads','208','208'),('DoNotUseThreads','209','209'),('DoNotUseThreads','210','210')};assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0
 classification=[]
 for f in findings:
  why='Independent null-contract negative clones fourteen canonical args then replaces exactly one reference; asserts reflected constructor cause NPE. No production null mutation.' if f['rule']=='NullAssignment' else 'Standalone host PT owns executor2/submits pure protocol work; both Future.get now ten-second bounded and compare independent literal golden bytes. No J2EE/container thread.'
  classification.append(dict(finding=f,classification='NOT_APPLICABLE',reason=why))
 saved=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22766-protocol-static-applicability-v1/manifest.json';prev=load(saved);assert prev['actualExit']==0;current={n:sha(R/n) for n in prev['inputHashes']};changed=[n for n in current if current[n]!=prev['inputHashes'][n]];assert changed==[original['path']];olditems=[x for x in prev['individualClassifications'] if x['finding']['path']==original['path']];assert len(olditems)==4
 strip=lambda f:{k:v for k,v in f.items() if k not in ['path','classification']};assert sorted(json.dumps(strip(v['finding']),sort_keys=True) for v in olditems)==sorted(json.dumps(v,sort_keys=True) for v in findings)
 retained=[v for v in prev['individualClassifications'] if v['finding']['path']!=original['path']];assert len(retained)==7;static25=dict(checkedSources=25,unchangedSources=24,changedSources=1,currentInputHashes=current,currentComposedRaw=11,classified=11,applicable=0,unclassified=0,checkstyle=0,formatDifferences=0,originalSnapshot=dict(path=str(saved.relative_to(R)),sha256=sha(saved)),retainedItems=retained,requalifiedItems=classification,freshAll25EngineRun=False,previousPendingBugResolvedByThisWhole12='BUG-2450')
 cp=RUNS/'pg22780-qa054-twelve-compile-v1/manifest.json';assert sha(cp)==b['compileManifestSha256'] and load(cp)['actualExit']==0 and load(cp)['inputHashes']==b['inputHashes']
 O.mkdir();files={}
 for base,prefix in [(U,'original-'),(S,'static-'),(META,'passive-')]:
  for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
   if p.is_file():
    name='jacoco.exec' if p.name=='jacoco.exec' else prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 (O/'protocol25-current-binding.json').write_text(json.dumps(static25,ensure_ascii=False,indent=2)+'\n');files['protocol25-current-binding.json']=sha(O/'protocol25-current-binding.json')
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=12,newUniqueTests=0,requalifiedExistingTests=12,newSourceProofs=0,newAcceptance=0,waitDeadlineAdditions=2,sourceTransformNegativeChecks=3,allOtherJavaTokensFixturesAndOracleUnchanged=True,coverage=cs,naturalBranchZero=True,branchCoverageRatio=None,branchAssessment='NATURAL_ZERO_NOT_MEASURED_PERCENT',physical={TARGET:allhashes[TARGET]},classIds={TARGET:allids[TARGET]},rawProbes={TARGET:probes[TARGET]},standardFilters=['JaCoCo RecordFilter generated accessors/ObjectMethods only; custom canonical/legacy constructor/from/fields/redacted toString all counted'],manualExclusions=[],physicalProductInitializations=sorted(normalInit),jvmGeneratedLambdaOwners={n:lambda_owner(n) for n in sorted(generated)},lambdaOwnerNegativeGuards=3,backendRootNativeFourHeldActions=0,staticRaw=4,individualStaticClassifications=classification,staticApplicable=0,checkstyle=0,unchangedMainSpotbugs=sm['unchangedMainStaticSha256'],protocol25CurrentComposedStatic=static25,oldExecCombined=False,whole451Accepted=False,formalUpdated=False,effortRate=None,inputHashes=b['inputHashes'],environment=environment,files=files,bug='BUG-2450',yktStillOpen='YKT-2177',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requalified=12,newUnique=0,counters=cs,naturalBranchZero=True,normalInit=len(normalInit),generatedLambda=len(generated),static25classified=11,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
