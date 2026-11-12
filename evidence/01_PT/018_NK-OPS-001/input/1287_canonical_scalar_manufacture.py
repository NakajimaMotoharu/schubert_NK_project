"""Independent Python LP/HMAC golden input, two new whole-fixture methods; Main unchanged."""
from pathlib import Path
import hashlib,hmac,json,struct,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26622-canonical-scalar-fixture-v1';P=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/OperationFingerprintTest.java';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not O.exists();old=P.read_text();assert old.count('@Test')==5
lp=lambda b:struct.pack('>I',len(b))+b
vectors=[]
for scalar in ['\U00010000','\U0010ffff']:
 value=('é'+scalar).encode('utf-8');number=b'-9223372036854775808';canon=b'SCHUBERT-NK-OP1'+b''.join(lp(v) for v in [b'7',b'QSTREQ01',b'001',('QUESTION:'+scalar).encode('utf-8')])+struct.pack('>I',2)+lp(b'text')+lp(b'X1')+lp(value)+lp(b'number')+lp(b'N1')+lp(number)
 vectors.append(dict(codepoint=ord(scalar),textHex=value.hex(),canonicalHex=canon.hex(),hmacSha256=hmac.new(bytes(32),canon,hashlib.sha256).hexdigest()))
bad=['\\ud800','\\udc00','\\ud800\\ud800','\\udc00\\udc00','a\\ud800','\\udc00a','\\ud800b\\udc00','\\ud800\\udc00\\ud800']
addition='''
  /** PT-IDEM-U1601; SS3243/BUG2669/YKT2349: 24 independent invalid scalar boundaries. */
  @Test
  void scalar001MalformedTextNeverAliasesQuestionMarkInCanonicalInput() {
    var checks = new ArrayList<org.junit.jupiter.api.function.Executable>();
    for (String value : List.of(BAD_VALUES)) {
      checks.add(() -> assertThrows(IllegalArgumentException.class,
          () -> CanonicalField.text("text", value)));
      checks.add(() -> assertThrows(IllegalArgumentException.class,
          () -> new CanonicalRequest(value, QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, "t", List.of())));
      checks.add(() -> assertThrows(IllegalArgumentException.class,
          () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, value, List.of())));
    }
    org.junit.jupiter.api.Assertions.assertAll(checks);
    assertThrows(NullPointerException.class, () -> CanonicalField.text("text", null));
  }

  /** PT-IDEM-U1602; Python struct/HMAC vectors, no production-derived expected bytes. */
  @Test
  void scalar002SupplementaryNfcAndSignedNumberMatchIndependentVectors() {
    String[] scalars = {"\\ud800\\udc00", "\\udbff\\udfff"};
    String[] texts = {TEXT_HEX};
    String[] canonicals = {CANON_HEX};
    String[] digests = {HMAC_HEX};
    for (int index = 0; index < scalars.length; index++) {
      try (var text = CanonicalField.text("text", "e\\u0301" + scalars[index]);
          var number = CanonicalField.number("number", Long.MIN_VALUE);
          var request = new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION,
              "QUESTION:" + scalars[index], List.of(text, number))) {
        assertArrayEquals(HEX.parseHex(texts[index]), text.value());
        assertArrayEquals("-9223372036854775808".getBytes(StandardCharsets.US_ASCII), number.value());
        assertArrayEquals(HEX.parseHex(canonicals[index]), OperationFingerprint.INSTANCE.canonicalBytes(request));
        assertArrayEquals(HEX.parseHex(digests[index]), OperationFingerprint.INSTANCE.calculate(request, new byte[32]));
      }
    }
  }
'''
addition=addition.replace('BAD_VALUES',', '.join('"'+s+'"' for s in bad))
for name,key in [('TEXT_HEX','textHex'),('CANON_HEX','canonicalHex'),('HMAC_HEX','hmacSha256')]:addition=addition.replace(name,', '.join('"'+v[key]+'"' for v in vectors))
insert=old.index('  private static int providerPosition');new=old[:insert]+addition+'\n'+old[insert:];assert new.count('@Test')==7;P.write_text(new)
jdk=R.parent/'toolchain/jdk-25.0.4/bin/java';fmt=R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'
if not fmt.exists():fmt=next((R.parent/'toolchain').rglob('google-java-format-1.36.1-all-deps.jar'))
a=subprocess.run([str(jdk),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert a.returncode==0,a.stderr;P.write_text(a.stdout)
O.mkdir();(O/'original-operation-test.txt').write_text(old);(O/'independent-vectors.json').write_text(json.dumps(dict(format='SS3243 NKOP1 big-endian LP NFCUTF8',generator='Python struct.pack and hmac.sha256 only, no JVM/product methods',publicSyntheticZeroKey=True,malformedUtf16JavaLiterals=bad,vectors=vectors),ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,inputPath=str(P.relative_to(R)),originalTests=5,newTests=2,totalWholeOperationTests=7,originalSha256=sha(O/'original-operation-test.txt'),newSha256=sha(P),secretBufferOriginalWholeTests=3,originalMainUnchanged=True,productTestsExecuted=0,independentVectorSha256=sha(O/'independent-vectors.json'),verifierSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value))
