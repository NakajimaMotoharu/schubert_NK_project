"""Pure value fixtures and independent six-field AAD literal; no claimed-row dependency or key action."""
from pathlib import Path
import ast,hashlib,json,struct,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/';names=['RevocationPayloadIdentity','EncryptedRevocationPayload','RevocationFailureCode','RevocationRetryException','RevocationPayloadException'];main=[base+n+'.java' for n in names];oldtest='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/revocation/ExceptionValueContractTest.java';oldsha=sha(r/oldtest);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/revocation/RevocationValueContractTest.java';assert not p.exists();assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[oldtest]);fields=[b'web-revoke',b'schubert_web_session.pending_context_revocations',bytes(range(16)),struct.pack('>qi',-1,123456000),bytes([1]),b'v1'];golden=b''.join(struct.pack('>I',len(v))+v for v in fields)
original=ast.parse((b/'input/3860_web_log_value5_source.py').read_text());raw=next(n.value.func.value.value for n in original.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='s' for t in n.targets));a=raw.index('  @Test\n  void value002');z=raw.index('  @Test\n  void value003',a);cipher=raw[a:z].replace('value002','revokevalue002').replace('EncryptedWebLogPayload','EncryptedRevocationPayload').replace('29, 30, 2387, 2388','29, 30, 115, 116').replace('0, 28, 2389','0, 28, 117').replace('EncryptedRevocationPayload[keyVersion=v1, ciphertext=<redacted>]','EncryptedRevocationPayload[REDACTED]')
s='''package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-REVOKE-VALUE001..004; QA050/SS331352: synthetic identity/bytes only, no retry/crypto/key/DB. */
final class RevocationValueContractTest {
  private static final String VERSION = "v1";
  private static final String STORED = "owned-value";
  private static final UUID ID = new UUID(0x0001020304050607L, 0x08090a0b0c0d0e0fL);
  private static final Instant REQUESTED = Instant.ofEpochSecond(-1, 123456000);
  private static final RevocationPayloadIdentity IDENTITY = new RevocationPayloadIdentity(ID, REQUESTED);
  private static final String AAD_HEX = "GOLDEN_HEX";

  @Test
  void revokevalue001IdentityUsesAllUuidAndTimeBitsAndIndependentSixFieldAad() {
    var equal = new RevocationPayloadIdentity(ID, REQUESTED);
    assertEquals(ID, IDENTITY.id());
    assertEquals(REQUESTED, IDENTITY.requestedAt());
    assertEquals(IDENTITY, equal);
    assertEquals(IDENTITY.hashCode(), equal.hashCode());
    assertEquals(STORED, Map.of(IDENTITY, STORED).get(equal));
    assertNotEquals(IDENTITY, new RevocationPayloadIdentity(new UUID(0, 1), REQUESTED));
    assertNotEquals(IDENTITY, new RevocationPayloadIdentity(ID, Instant.EPOCH));
    assertNotEquals(IDENTITY, null);
    assertNotEquals(IDENTITY, VERSION);
    assertEquals("RevocationPayloadIdentity[REDACTED]", IDENTITY.toString());
    byte[] expected = HexFormat.of().parseHex(AAD_HEX);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    byte[] returned = IDENTITY.aad(VERSION);
    Arrays.fill(returned, (byte) 0);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    for (Instant at : List.of(Instant.EPOCH, Instant.ofEpochSecond(1, 999999000)))
      assertEquals(at, new RevocationPayloadIdentity(ID, at).requestedAt());
    assertThrows(IllegalArgumentException.class, () -> new RevocationPayloadIdentity(ID, Instant.EPOCH.plusNanos(1)));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(null, REQUESTED));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(ID, null));
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
  }

CIPHER_METHOD
  @Test
  void revokevalue003FailureCodesHaveFixedLookupDefensiveValuesAndRetryDiagnostic() {
    var values = List.of(RevocationFailureCode.SESSION_INVALID, RevocationFailureCode.API_REJECTED,
        RevocationFailureCode.INVALID_RESPONSE, RevocationFailureCode.UNAVAILABLE,
        RevocationFailureCode.KEY_UNAVAILABLE, RevocationFailureCode.PAYLOAD_INVALID,
        RevocationFailureCode.CRYPTO_UNAVAILABLE);
    var names = List.of("SESSION_INVALID", "API_REJECTED", "INVALID_RESPONSE", "UNAVAILABLE",
        "KEY_UNAVAILABLE", "PAYLOAD_INVALID", "CRYPTO_UNAVAILABLE");
    assertEquals(values, List.of(RevocationFailureCode.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), RevocationFailureCode.valueOf(names.get(index)));
    }
    var copy = RevocationFailureCode.values();
    copy[0] = RevocationFailureCode.UNAVAILABLE;
    assertSame(RevocationFailureCode.SESSION_INVALID, RevocationFailureCode.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "session_invalid", "SESSION_INVALID "))
      assertThrows(IllegalArgumentException.class, () -> RevocationFailureCode.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> RevocationFailureCode.valueOf(null));
    var retry = new RevocationRetryException();
    assertEquals("retained revocation retry infrastructure unavailable", retry.getMessage());
    assertNull(retry.getCause());
    assertEquals(0, retry.getSuppressed().length);
  }

  @Test
  void revokevalue004PayloadReasonsHaveExactDiagnosticNamesAndDefensiveValues() {
    var values = List.of(RevocationPayloadException.Reason.PAYLOAD_INVALID,
        RevocationPayloadException.Reason.KEY_UNAVAILABLE, RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE);
    var names = List.of("PAYLOAD_INVALID", "KEY_UNAVAILABLE", "CRYPTO_UNAVAILABLE");
    assertEquals(values, List.of(RevocationPayloadException.Reason.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), RevocationPayloadException.Reason.valueOf(names.get(index)));
      var failure = new RevocationPayloadException(values.get(index));
      assertEquals("revocation encrypted payload rejected: " + names.get(index), failure.getMessage());
      assertSame(values.get(index), failure.reason());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    var copy = RevocationPayloadException.Reason.values();
    copy[0] = RevocationPayloadException.Reason.KEY_UNAVAILABLE;
    assertSame(RevocationPayloadException.Reason.PAYLOAD_INVALID, RevocationPayloadException.Reason.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "payload_invalid", "PAYLOAD_INVALID "))
      assertThrows(IllegalArgumentException.class, () -> RevocationPayloadException.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> RevocationPayloadException.Reason.valueOf(null));
  }
}
'''.replace('GOLDEN_HEX',golden.hex()).replace('CIPHER_METHOD',cipher);p.write_text(s);subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert sha(r/oldtest)==oldsha;out=b/'evidence/PG34680-revocation-value5-source-v1';out.mkdir();targets=['dev/codex/schubert/nk/web/revocation/'+n for n in names+['RevocationPayloadException$Reason']];v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=4),dict(path=oldtest,tests=1)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r)),oldtest]},sdkHashes={},mainSourcesUnchanged=True,oldExceptionOneByteExact=True,oldTestSha256=oldsha,newDefinitions=4,necessaryPriorDefinitions=1,expectedTests=5,targets=targets,independentAad=dict(spec='SS331352 six32bit BE length prefixes/UUID BE/seconds signed64 BE+nanos signed32 BE, independent literal Python struct',fieldsHex=[v.hex() for v in fields],fieldLengths=[len(v) for v in fields],length=len(golden),goldenHex=golden.hex()),claimedRevocationNotCompiledOrExtracted=True,applicationTestsExecuted=0,newAcceptance=0,noWholeWebOrApiJarPayloadAccess=True);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=5,tests=5,newDefinitions=4,aadLength=len(golden),originalException1Unchanged=True)))
