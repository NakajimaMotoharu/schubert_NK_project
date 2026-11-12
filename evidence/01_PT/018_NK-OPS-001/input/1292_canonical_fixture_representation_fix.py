"""Same UTF16 units, no malformed Java StringLiteral decoded into PMD XPath/Saxon strings."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';P=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/OperationFingerprintTest.java';O=B/'evidence/PG26639-canonical-fixture-representation-v1';assert not O.exists();old=P.read_text();s=old
units=[[0xd800],[0xdc00],[0xd800,0xd800],[0xdc00,0xdc00],[0x61,0xd800],[0xdc00,0x61],[0xd800,0x62,0xdc00],[0xd800,0xdc00,0xd800]]
gold=json.loads((B/'evidence/PG26622-canonical-scalar-fixture-v1/independent-vectors.json').read_text());assert len(gold['malformedUtf16JavaLiterals'])==len(units)==8
for original,row in zip(gold['malformedUtf16JavaLiterals'],units):
 decoded=original.encode().decode('unicode_escape');assert [int.from_bytes(decoded.encode('utf-16-be','surrogatepass')[i:i+2],'big') for i in range(0,len(decoded.encode('utf-16-be','surrogatepass')),2)]==row
 token='"'+original+'"';assert token in s;s=s.replace(token,'new String(new char[] {'+', '.join(hex(x) for x in row)+'})',1)
for token,cp in [('"\\ud800\\udc00"',0x10000),('"\\udbff\\udfff"',0x10ffff)]:assert token in s;s=s.replace(token,'Character.toString('+hex(cp)+')',1)
jdk=R.parent/'toolchain/jdk-25.0.4/bin/java';fmt=next((R.parent/'toolchain').rglob('google-java-format-1.36.1-all-deps.jar'));a=subprocess.run([str(jdk),'-jar',str(fmt),'-'],input=s,text=True,capture_output=True);assert a.returncode==0;P.write_text(a.stdout);O.mkdir();(O/'test-before.txt').write_text(old);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0,beforeSha256=sha(O/'test-before.txt'),afterSha256=sha(P),independentSameUtf16UnitRows=units,validCodepoints=[x['codepoint'] for x in gold['vectors']],expectedGoldenAndAssertionsChanged=False,originalFiveAndSecretThreeChanged=False,productTestsExecuted=0);(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sameInvalidRows=8,valid2=True,unitReplayed=False)))
