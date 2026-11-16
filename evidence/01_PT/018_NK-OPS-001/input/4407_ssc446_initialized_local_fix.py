"""Refine the approved pure dispatch placement without changing constructor validation or expectations."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';pub=json.loads((b/'evidence/PG36542-ssc446-compile-design-main-v2/manifest.json').read_text());assert pub['actualExit']==0;subprocess.run(['git','merge-base','--is-ancestor',pub['designSource'],'origin/main'],check=True)
t=r/'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/FieldDefinition.java';old=t.read_text();assert t.read_bytes()==(b/'evidence/PG36539-ssc446-root-compile-failure-v1/FieldDefinition.before.java.txt').read_bytes()
inline='''    final Padding expected;
    if (wireType == WireType.TEXT) {
      expected = Padding.SPACE_RIGHT;
    } else if (wireType == WireType.NUMERIC) {
      expected = Padding.ZERO_LEFT;
    } else {
      expected = Padding.NONE;
    }
'''
helper='''  private static Padding expectedPaddingFor(WireType wireType) {
    if (wireType == WireType.TEXT) {
      return Padding.SPACE_RIGHT;
    } else if (wireType == WireType.NUMERIC) {
      return Padding.ZERO_LEFT;
    } else {
      return Padding.NONE;
    }
  }

'''
init='    final Padding expected = expectedPaddingFor(wireType);\n';anchor='  private static int checkedEnd(int start, int length) {';assert old.count(inline)==old.count(anchor)==1
new=old.replace(inline,init).replace(anchor,helper+anchor);assert new.replace(helper,'').replace(init,inline)==old;t.write_text(new)
subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(t)],check=True,timeout=30)
assert t.read_text()==new
original=(b/'evidence/PG36504-ssc446-field-padding-source-v1/FieldDefinition.before.java.txt').read_text();switch='''    Padding expected =
        switch (wireType) {
          case TEXT -> Padding.SPACE_RIGHT;
          case NUMERIC -> Padding.ZERO_LEFT;
          case BOOLEAN -> Padding.NONE;
        };
''';assert new.replace(helper,'').replace(init,switch)==original
oldproof=json.loads((b/'evidence/PG36504-ssc446-field-padding-source-v1/manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));assert all(sha(r/n)==h for n,h in oldproof['other164MainAndAllTestsResourcesUnchanged'].items())
e=b/'evidence/PG36544-ssc446-initialized-local-source-v2';e.mkdir();(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,bug='BUG3123',ykt='YKT2595',approvedDesign=pub,previousFailedSource=ref(b/'evidence/PG36539-ssc446-root-compile-failure-v1/FieldDefinition.before.java.txt'),sourceAfter=ref(t),wholeOriginalSwitchBodyDiagnosticsInverseByteExact=True,other164MainAllTestsResourcesUnchanged=True,publicApiUnchangedRequired=True,newPrivatePureMethod=1,newJUnitDefinitions=0,productTestsExecuted=0,rootCompilerFlagsRelaxed=False,standaloneJdkBugClaimed=False),indent=2)+'\n')
print(json.dumps(dict(actualExit=0,inverseOriginalBodyExact=True,newPrivatePureMethod=1,mainChanged=1,newTests=0)))
