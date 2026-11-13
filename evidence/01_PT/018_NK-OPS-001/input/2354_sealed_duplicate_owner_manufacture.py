"""BUG2840 source repair and an unexecuted whole-Test case; no native/product invocation."""
from pathlib import Path
import datetime,hashlib,json,subprocess,xml.etree.ElementTree as X
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29578-sealed-duplicate-source-manufacture-v1';o.mkdir();base=Path('src/schubert-nk-storage/src');main=base/'main/java/dev/codex/schubert/nk/storage/LinuxSealedProof.java';test=base/'test/java/dev/codex/schubert/nk/storage/LinuxSealedProofTest.java';m=(r/main).read_text();t=(r/test).read_text();(o/'LinuxSealedProof.before.java.txt').write_text(m);(o/'LinuxSealedProofTest.before.java.txt').write_text(t)
a='() -> new Descriptor(() -> fcntl.call(descriptor, 1030, 128)), // F_DUPFD_CLOEXEC';z='() -> new Descriptor(() -> duplicateReserved(descriptor)), // F_DUPFD_CLOEXEC';assert m.count(a)==1;newm=m.replace(a,z)
marker='  /**\n   * Borrows an already root-admitted FD.'
helper='''  // SS333/BUG2840: the original FD is already owned, not a newly acquired duplicate.
  private int duplicateReserved(int original) {
    int reserved = fcntl.call(original, 1030, 128);
    return reserved == original ? -1 : reserved;
  }

''';assert newm.count(marker)==1;newm=newm.replace(marker,helper+marker)
newtest='''  /** PT-OPS-SEAL-009: alias results create no second owner; native Test HOLD remains. */
  @Test
  void opsSeal009SameDescriptorResultNeverCreatesSecondOwner() {
    for (int original : List.of(128, 129, 65535)) {
      var fixture = new Fixture(VECTOR);
      fixture.original = original;
      fixture.reserved = original;
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> fixture.calls().withProof(VECTOR, fd -> fail("aliased owner callback"))));
      assertArrayEquals(VECTOR, fixture.written.toByteArray());
      assertEquals(
          List.of(
              FIXTURE_CREATE_5498A731,
              "mode:" + original + ":384",
              "write:" + original,
              "fcntl:" + original + ":1033:15",
              "fcntl:" + original + ":1030:128",
              "close:" + original),
          fixture.events);
    }
  }

'''
pairs=[('  private static void unavailable(StorageIoException failure) {',newtest+'  private static void unavailable(StorageIoException failure) {'),('    int reserved = 129;','    int reserved = 129;\n    int original = 17;'),('return failed.equals(FIXTURE_CREATE_5498A731) ? -1 : 17;','return failed.equals(FIXTURE_CREATE_5498A731) ? -1 : original;')];newt=t
for a1,z1 in pairs:assert newt.count(a1)==1;newt=newt.replace(a1,z1)
assert m.count('@Test')==0 and t.count('@Test')==8 and newt.count('@Test')==9
inv=newt
for a1,z1 in reversed(pairs):assert inv.count(z1)==1;inv=inv.replace(z1,a1)
assert inv==t and newm.replace(helper,'').replace(z,a)==m
(r/main).write_text(newm);(r/test).write_text(newt)
tc=r.parent/'toolchain';java=tc/'jdk-25.0.4/bin/java';gjf=tc/'google-java-format-1.36.1-all-deps.jar';cs=tc/'static-gates-20261015/checkstyle-14.3.0-all.jar';fmt=[str(java),'-jar',str(gjf),'--skip-reflowing-long-strings'];commands=[]
for label,args in [('format',fmt+['--replace',str(r/main),str(r/test)]),('format-check',fmt+['--dry-run','--set-exit-if-changed',str(r/main),str(r/test)]),('checkstyle',[str(java),'-jar',str(cs),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(o/'checkstyle.xml'),str(r/main),str(r/test)])]:
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (o/(label+'.stdout')).open('xb') as out,(o/(label+'.stderr')).open('xb') as err:
  child=subprocess.Popen(args,cwd=r,stdout=out,stderr=err,stdin=subprocess.DEVNULL);owner=__import__('os').getpid();code=child.wait(timeout=180)
 commands.append(dict(label=label,command=args,pid=child.pid,ownerPid=owner,startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=code));assert code==0
assert not X.parse(o/'checkstyle.xml').findall('.//error')
normalize=lambda text:subprocess.check_output(fmt+['-'],input=text.encode())
assert normalize(inv)==normalize(t) and normalize(newm.replace(helper,'').replace(z,a))==normalize(m)
assert (r/main).read_bytes()==normalize(newm) and (r/test).read_bytes()==normalize(newt)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mout=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMainBefore='8b539471183a640ad4a2541ee06a1eb1717199fc',MainChanged=1,newDefinitions=1,newQualifiedDefinitions=0,wholeOriginalDefinitions=8,wholeCurrentDefinitions=9,oldWholeEightNormalizedInverseEqual=True,oldWholeMainNormalizedInverseEqual=True,sourceGjfCheckstyle0=True,inputHashes={str(p):sha(r/p) for p in [main,test]},toolHashes={str(p):sha(p) for p in [java,gjf,cs,r/'tools/quality/static/checkstyle.xml']},commands=commands,independentAliasInputs=[128,129,65535],expectedState='SAME_FD_NOT_NEW_OWNERSHIP; CALLBACK0; ORIGINAL_CLOSE1',productTestsExecuted=0,coverage=None,wholeTestRuntime='HOLD_NOT_RUN_NO_EXTRACTION',actualNativeFdRootVmDbKeyOperations=0,bug='BUG-2840',horizontal='YKT-2404',bugState='SOURCE_FIXED_STATIC_MORE_PENDING_RUNTIME_NOT_RUN')
(o/'manifest.json').write_text(json.dumps(mout,ensure_ascii=False,indent=2)+'\n');print('one Main repaired, original8 inverse-equal, new1 Testsource NOT_RUN; GJF/CS0; no native/Product execution')
