"""Public ABI18 unchanged, target privateguard/linear choice only, original eight fixture bodies retained."""
from pathlib import Path
import datetime,hashlib,json,subprocess
import pg9666_pagination_static as c
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base=ld(b/'evidence/PG38140-media-decoder-before-source-v1/manifest.json');before=b/'evidence/PG38142-media-before-prepare-v1';after=b/'evidence/PG38146-media-after-prepare-v1';bm=ld(before/'manifest.json');am=ld(after/'manifest.json');assert bm['actualExit']==am['actualExit']==0;out=b/'evidence/PG38150-media-decoder-abi-body-v1';assert not out.exists();out.mkdir();c.SLOT=out;rows=[]
for n,h in base['mainHashes'].items():
 previous=subprocess.check_output(['git','show',base['sourceCore']+':'+n]).decode();assert hashlib.sha256(previous.encode()).hexdigest()==h;current=(r/n).read_text();inverse=current
 if n.endswith('/MediaResponseDecoder.java'):
  oldstart=previous.index('    return switch (layout) {');oldend=previous.index('\n  private static boolean sameContext',oldstart);newstart=current.index('    if (layout.equals("AUDREQ01")) {');newend=current.index('\n  private static boolean sameContext',newstart);inverse=current[:newstart]+previous[oldstart:oldend]+current[newend:];inverse=inverse.replace('private MediaResponseDecoder() {\n    throw new AssertionError("static namespace");\n  }','private MediaResponseDecoder() {}')
 assert inverse==previous;rows.append(dict(path=n,beforeSha256=h,afterSha256=sha(r/n),privateGuardAndLinearSelectionOnlyInverseExact=True,unchanged=not n.endswith('/MediaResponseDecoder.java')))
fixtures=[]
for n,h in base['testHashes'].items():
 previous=subprocess.check_output(['git','show',base['sourceCore']+':'+n]);assert hashlib.sha256(previous).hexdigest()==h;text=(r/n).read_text();inverse=text
 if n.endswith('/MediaVerifiedProjectionTest.java'):
  start=text.index('  @Test\n  void hashCollisionLayoutsNeverAcquireAProjectionFromALegitimateResult()');end=text.index('  private static void reject(',start);inverse=text[:start]+text[end:];inverse=inverse.replace('import static org.junit.jupiter.api.Assertions.assertNotEquals;\n','')
 assert inverse.encode()==previous;fixtures.append(dict(path=n,existingWhole4BusinessBodyInverseExact=True,beforeSha256=h,afterSha256=sha(r/n)))
abi=[]
for n in bm['mainClassHashes']:
 a=before/('abi-'+Path(n).stem+'.stdout');z=after/('abi-'+Path(n).stem+'.stdout');assert a.read_bytes()==z.read_bytes();abi.append(dict(className=n,publicAbiEqual=True,before=ref(a),after=ref(z)))
targets={n for n in bm['mainClassHashes'] if '/media/MediaResponseDecoder' in n};assert len(targets)==3;shared={n:h for n,h in am['physicalClassHashes'].items() if n not in targets};assert len(shared)==191 and all(bm['physicalClassHashes'][n]==h for n,h in shared.items());nested=[]
for binary in sorted(n for n in targets if '$' in n):
 name=binary[:-6].replace('/','.');label=Path(binary).stem
 for phase,m in [('before',bm),('after',am)]:
  step=c.step(phase+'-code-'+label,[str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-c','-p','-classpath',str(Path(m['work'])/'component'),name],r);assert step['actualExit']==0
 assert (out/('before-code-'+label+'.stdout')).read_bytes()==(out/('after-code-'+label+'.stdout')).read_bytes();nested.append(dict(className=binary,allVisibilityInstructionDisassemblyEqual=True,lineTableChangesOnlyNotBusinessCode=True))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCoreBefore=base['sourceCore'],main10Rows=rows,publicAbi18Equal=abi,original8FixtureBusinessBodyInverseExact=fixtures,shared191PhysicalByteExact=True,targetNested2InstructionDisassemblyEqual=nested,onlyNewCaseDefinitions=2,actualJmsBrokerSessionConnectionHttpFileKeyDbVmRootNativeAuthorityActions=0,privateResultReflectionOrForgery=False,productTestsExecuted=0,before=ref(before/'manifest.json'),after=ref(after/'manifest.json'));(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,ABI18=18,MainInverse10=10,Original8BodyInverse=True,shared191SameBytes=True,nested2CodeSame=True))
