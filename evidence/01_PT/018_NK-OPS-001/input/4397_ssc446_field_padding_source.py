"""Implement only the approved closed-three padding dispatch, with an exact inverse."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';pub=json.loads((b/'evidence/PG36502-ssc446-design-main-publication-v1/manifest.json').read_text());assert pub['actualExit']==0 and pub['ssc']=='SSC446'
subprocess.run(['git','merge-base','--is-ancestor',pub['designSource'],'origin/main'],check=True)
oldcore='7f04f07fb43c6fac322808fa3251d4f1b95e44ae';base=r/'src/schubert-nk-protocol/src';t=base/'main/java/dev/codex/schubert/nk/protocol/layout/FieldDefinition.java';old=t.read_text();assert t.read_bytes()==subprocess.check_output(['git','show',oldcore+':'+str(t.relative_to(r))])
oldblock='''    Padding expected =
        switch (wireType) {
          case TEXT -> Padding.SPACE_RIGHT;
          case NUMERIC -> Padding.ZERO_LEFT;
          case BOOLEAN -> Padding.NONE;
        };
'''
newblock='''    final Padding expected;
    if (wireType == WireType.TEXT) {
      expected = Padding.SPACE_RIGHT;
    } else if (wireType == WireType.NUMERIC) {
      expected = Padding.ZERO_LEFT;
    } else {
      expected = Padding.NONE;
    }
'''
assert old.count(oldblock)==1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));others=[p for p in (base/'main/java').rglob('*.java') if p!=t]+list((base/'test').rglob('*'));others=[p for p in others if p.is_file()];before={str(p.relative_to(r)):sha(p) for p in others}
e=b/'evidence/PG36504-ssc446-field-padding-source-v1';e.mkdir();(e/'FieldDefinition.before.java.txt').write_text(old);t.write_text(old.replace(oldblock,newblock))
subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(t)],check=True,timeout=30)
new=t.read_text();assert new.count(newblock)==1 and new.replace(newblock,oldblock)==old
assert before=={str(p.relative_to(r)):sha(p) for p in others}
(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,previousCore=oldcore,sourceBefore=ref(e/'FieldDefinition.before.java.txt'),sourceAfter=ref(t),approvedDesign=pub,wholeBodyDiagnosticsInverseByteExact=True,onlyChangedMain=str(t.relative_to(r)),other164MainAndAllTestsResourcesUnchanged=before,newTestDefinitions=0,oldSourceOrExecSuccessTransferred=False,productTestsExecuted=0,expectedPhysicalChange=dict(old=176,new=175,removedOnly='dev/codex/schubert/nk/protocol/layout/FieldDefinition$1.class',other174BytesUnchangedRequired=True),whole451Accepted=False),indent=2)+'\n')
print(json.dumps(dict(actualExit=0,mainChanged=1,newTests=0,inverseWholeBodyExact=True,unchangedSourceFiles=len(before))))
