"""Give the two immutable caches real private state owners and prove full formatted source inversion."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';pub=json.loads((b/'evidence/PG36602-ssc447-cache-owners-design-main-v1/manifest.json').read_text());assert pub['actualExit']==0;subprocess.run(['git','merge-base','--is-ancestor',pub['designSource'],'origin/main'],check=True)
base=r/'src/schubert-nk-protocol/src';paths=[base/'main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java',base/'main/java/dev/codex/schubert/nk/protocol/time/JstWireTimestamp.java'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));others=[p for p in (base/'main/java').rglob('*.java') if p not in paths]+[p for p in (base/'test').rglob('*') if p.is_file()];unchanged={str(p.relative_to(r)):sha(p) for p in others};callers=json.loads((b/'evidence/PG36600-ssc447-cache-owners-design-only-v1/all-callers-source-witness.json').read_text());assert all(sha(r/x['path'])==x['sha256'] for x in callers['callers'])
e=b/'evidence/PG36604-ssc447-cache-owner-source-v1';e.mkdir();jdk=r.parent/'toolchain/jdk-25.0.4/bin/java';gjf=r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar';proofs=[]
typedOld='''  private static final Pattern OPTIONAL_ID = Pattern.compile("[0-9]{1,12}");

  private TypedFieldValues() {}
'''
typedNew='''  private static final TypedFieldValues INSTANCE = new TypedFieldValues();
  private final Pattern retainedOptionalId;

  private TypedFieldValues() {
    retainedOptionalId = Pattern.compile("[0-9]{1,12}");
  }
'''
jstOld='''  private static final ZoneId JAPAN = ZoneId.of("Asia/Tokyo");
  private static final Pattern DIGITS = Pattern.compile("[0-9]{17}");
  private static final DateTimeFormatter FORMATTER =
      DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS").withResolverStyle(ResolverStyle.STRICT);

  private JstWireTimestamp() {}
'''
jstNew='''  private static final JstWireTimestamp INSTANCE = new JstWireTimestamp();
  private final ZoneId retainedJapanZone;
  private final Pattern retainedWireDigits;
  private final DateTimeFormatter retainedWireFormatter;

  private JstWireTimestamp() {
    retainedJapanZone = ZoneId.of("Asia/Tokyo");
    retainedWireDigits = Pattern.compile("[0-9]{17}");
    retainedWireFormatter =
        DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS").withResolverStyle(ResolverStyle.STRICT);
  }
'''
for p,oldBlock,newBlock,bindings in [(paths[0],typedOld,typedNew,[('OPTIONAL_ID','INSTANCE.retainedOptionalId',1)]),(paths[1],jstOld,jstNew,[('JAPAN','INSTANCE.retainedJapanZone',2),('DIGITS','INSTANCE.retainedWireDigits',2),('FORMATTER','INSTANCE.retainedWireFormatter',2)])]:
 old=p.read_text();assert p.read_bytes()==subprocess.check_output(['git','show','a188e6683c8dcc5c81af43ecaeb9fc3b8f8f4ebd:'+str(p.relative_to(r))]);assert old.count(oldBlock)==1;before=e/(p.stem+'.before.java.txt');before.write_text(old);new=old.replace(oldBlock,newBlock)
 for name,value,count in bindings:
  assert len(re.findall(r'\b'+name+r'\b',new))==count
  new=re.sub(r'\b'+name+r'\b',value,new)
 p.write_text(new);subprocess.run([str(jdk),'-jar',str(gjf),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30)
 current=p.read_text();inverse=current
 for name,value,count in bindings:
  assert inverse.count(value)==count;inverse=inverse.replace(value,name)
 assert inverse.count(newBlock)==1;inverse=inverse.replace(newBlock,oldBlock)
 result=subprocess.run([str(jdk),'-jar',str(gjf),'--skip-reflowing-long-strings','-'],input=inverse,capture_output=True,text=True,check=True,timeout=30);assert result.stdout==old
 proofs.append(dict(before=ref(before),after=ref(p),formattedWholeBodyInverseExact=True,originalCacheLiteralAndOrderPreserved=True,publicStaticApisUnchangedRequired=True,realPrivateFinalStateConstructor=True,privateConstructorInvokedDirectlyByTest=False))
assert unchanged=={str(p.relative_to(r)):sha(p) for p in others};assert all(sha(r/x['path'])==x['sha256'] for x in callers['callers'])
(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,approvedDesign=pub,previousCore='a188e6683c8dcc5c81af43ecaeb9fc3b8f8f4ebd',parentProofs=proofs,allOther163MainTestsResourcesUnchanged=unchanged,all72CallersSourceUnchanged=True,originalCacheCompileAndOrderPreserved=True,jlsClassInitializationAndFinalFieldPublicationRetained=True,heapPerformanceMeasured=False,newTestDefinitions=0,productTestsExecuted=0,whole451Accepted=False),indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedMain=2,formattedInverseExact=True,callers=72,newTests=0)))
