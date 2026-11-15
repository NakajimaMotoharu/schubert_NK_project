"""Create independent value/AAD tests only. Fixed eight-field golden is computed without product code."""
from pathlib import Path
import hashlib,json,struct,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/';main=[base+n+'.java' for n in ['WebLogPayloadIdentity','EncryptedWebLogPayload','ClaimedWebLog','WebLogPayloadException']];oldtest='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/ExceptionValueContractTest.java';oldsha=sha(r/oldtest);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogValueContractTest.java';assert not p.exists();assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[oldtest]);fields=[b'web-log-outbox',b'schubert_web_session.web_log_outbox',bytes(range(16)),bytes(range(16,32)),bytes([1]),b'v1',b'WLGEVT01',b'001'];golden=b''.join(struct.pack('>I',len(v))+v for v in fields)
s='''package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-WLOG-VALUE001..004; SS324331352: public synthetic row bytes, no crypto/key/DB/backend. */
final class WebLogValueContractTest {
  private static final String VERSION = "v1";
  private static final String WORKER = "public-worker";
  private static final String STORED = "owned-value";
  private static final UUID MESSAGE = new UUID(0x0001020304050607L, 0x08090a0b0c0d0e0fL);
  private static final UUID CORRELATION = new UUID(0x1011121314151617L, 0x18191a1b1c1d1e1fL);
  private static final Instant CREATED = Instant.EPOCH;
  private static final Instant NEXT = Instant.EPOCH.plusSeconds(1);
  private static final Instant UNTIL = Instant.EPOCH.plusSeconds(2);
  private static final WebLogPayloadIdentity IDENTITY = new WebLogPayloadIdentity(MESSAGE, CORRELATION);
  private static final EncryptedWebLogPayload PAYLOAD = new EncryptedWebLogPayload(VERSION, new byte[29]);
  private static final String AAD_HEX = "GOLDEN_HEX";

  @Test
  void value001IdentityIsCompleteAndAadMatchesIndependentEightFieldGolden() {
    var equal = new WebLogPayloadIdentity(MESSAGE, CORRELATION);
    assertEquals(MESSAGE, IDENTITY.messageId());
    assertEquals(CORRELATION, IDENTITY.correlationId());
    assertEquals(IDENTITY, equal);
    assertEquals(IDENTITY.hashCode(), equal.hashCode());
    assertEquals(STORED, Map.of(IDENTITY, STORED).get(equal));
    assertNotEquals(IDENTITY, new WebLogPayloadIdentity(CORRELATION, CORRELATION));
    assertNotEquals(IDENTITY, new WebLogPayloadIdentity(MESSAGE, MESSAGE));
    assertNotEquals(IDENTITY, null);
    assertNotEquals(IDENTITY, VERSION);
    assertEquals("WebLogPayloadIdentity[message/correlation=<redacted>]", IDENTITY.toString());
    byte[] expected = HexFormat.of().parseHex(AAD_HEX);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    byte[] returned = IDENTITY.aad(VERSION);
    Arrays.fill(returned, (byte) 0);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    assertThrows(NullPointerException.class, () -> new WebLogPayloadIdentity(null, CORRELATION));
    assertThrows(NullPointerException.class, () -> new WebLogPayloadIdentity(MESSAGE, null));
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
  }

  @Test
  void value002CiphertextOwnershipBoundsAndArrayReferenceEqualityRemainExplicit() {
    for (int length : List.of(29, 30, 2387, 2388)) {
      byte[] input = new byte[length];
      input[0] = 7;
      var value = new EncryptedWebLogPayload(VERSION, input);
      input[0] = 9;
      byte[] first = value.ciphertext();
      assertEquals(length, first.length);
      assertEquals(7, first[0]);
      first[0] = 11;
      assertEquals(7, value.ciphertext()[0]);
      assertNotSame(first, value.ciphertext());
      assertEquals(VERSION, value.keyVersion());
      assertEquals(value, value);
      assertEquals(STORED, Map.of(value, STORED).get(value));
      int originalHash = value.hashCode();
      value.ciphertext()[0] = 22;
      assertEquals(originalHash, value.hashCode());
      assertNotEquals(value, new EncryptedWebLogPayload(VERSION, value.ciphertext()));
      assertNotEquals(value, new EncryptedWebLogPayload("v2", value.ciphertext()));
      assertNotEquals(value, null);
      assertNotEquals(value, VERSION);
      assertEquals("EncryptedWebLogPayload[keyVersion=v1, ciphertext=<redacted>]", value.toString());
    }
    for (String version : List.of("A", "A".repeat(16), "A._-09"))
      assertEquals(version, new EncryptedWebLogPayload(version, new byte[29]).keyVersion());
    for (String version : List.of("", "_bad", "A".repeat(17), "é", "v1 ", "v1/"))
      assertThrows(IllegalArgumentException.class, () -> new EncryptedWebLogPayload(version, new byte[29]));
    for (int length : List.of(0, 28, 2389))
      assertThrows(IllegalArgumentException.class, () -> new EncryptedWebLogPayload(VERSION, new byte[length]));
    assertThrows(NullPointerException.class, () -> new EncryptedWebLogPayload(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedWebLogPayload(VERSION, null));
  }

  @Test
  void value003ClaimedRowHasAllEightComponentsAndRejectsEachInvalidBoundary() {
    var row = new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL);
    var equal = new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL);
    assertEquals(1, row.id());
    assertSame(IDENTITY, row.identity());
    assertSame(PAYLOAD, row.payload());
    assertEquals(0, row.attemptCount());
    assertEquals(NEXT, row.nextAttemptAt());
    assertEquals(CREATED, row.createdAt());
    assertEquals(WORKER, row.leaseOwner());
    assertEquals(UNTIL, row.leaseUntil());
    assertEquals(row, equal);
    assertEquals(row.hashCode(), equal.hashCode());
    var map = new HashMap<ClaimedWebLog, String>();
    map.put(row, STORED);
    assertEquals(STORED, map.get(equal));
    for (var other : List.of(
        new ClaimedWebLog(2, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL),
        new ClaimedWebLog(1, new WebLogPayloadIdentity(CORRELATION, MESSAGE), PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL),
        new ClaimedWebLog(1, IDENTITY, new EncryptedWebLogPayload(VERSION, new byte[29]), 0, NEXT, CREATED, WORKER, UNTIL),
        new ClaimedWebLog(1, IDENTITY, PAYLOAD, 1, NEXT, CREATED, WORKER, UNTIL),
        new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, UNTIL, CREATED, WORKER, UNTIL),
        new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, NEXT, WORKER, UNTIL),
        new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, "other-worker", UNTIL),
        new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, NEXT))) assertNotEquals(row, other);
    assertNotEquals(row, null);
    assertNotEquals(row, VERSION);
    assertEquals("ClaimedWebLog[identity/payload/lease=<redacted>]", row.toString());
    for (long id : List.of(1L, 999_999_999_999L))
      for (int attempt : List.of(0, 1, 99, 100))
        assertEquals(attempt, new ClaimedWebLog(id, IDENTITY, PAYLOAD, attempt, NEXT, CREATED, WORKER, UNTIL).attemptCount());
    for (long id : List.of(-1L, 0L, 1_000_000_000_000L))
      assertThrows(IllegalArgumentException.class, () -> new ClaimedWebLog(id, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL));
    for (int attempt : List.of(-1, 101))
      assertThrows(IllegalArgumentException.class, () -> new ClaimedWebLog(1, IDENTITY, PAYLOAD, attempt, NEXT, CREATED, WORKER, UNTIL));
    for (String worker : List.of("A", "A".repeat(64), "._-09"))
      assertEquals(worker, ClaimedWebLog.requireWorker(worker));
    for (String worker : List.of("", "A".repeat(65), "with space", "../worker", "é", "worker:"))
      assertThrows(IllegalArgumentException.class, () -> ClaimedWebLog.requireWorker(worker));
    assertThrows(NullPointerException.class, () -> ClaimedWebLog.requireWorker(null));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, null, PAYLOAD, 0, NEXT, CREATED, WORKER, UNTIL));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, IDENTITY, null, 0, NEXT, CREATED, WORKER, UNTIL));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, null, CREATED, WORKER, UNTIL));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, null, WORKER, UNTIL));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, null, UNTIL));
    assertThrows(NullPointerException.class, () -> new ClaimedWebLog(1, IDENTITY, PAYLOAD, 0, NEXT, CREATED, WORKER, null));
  }

  @Test
  void value004PayloadReasonHasFixedNamesLookupDefensiveValuesAndClosedDiagnostic() {
    var reasons = List.of(WebLogPayloadException.Reason.KEY_UNAVAILABLE,
        WebLogPayloadException.Reason.PAYLOAD_INVALID, WebLogPayloadException.Reason.CRYPTO_UNAVAILABLE);
    var names = List.of("KEY_UNAVAILABLE", "PAYLOAD_INVALID", "CRYPTO_UNAVAILABLE");
    assertEquals(reasons, List.of(WebLogPayloadException.Reason.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), reasons.get(index).name());
      assertSame(reasons.get(index), WebLogPayloadException.Reason.valueOf(names.get(index)));
      var failure = new WebLogPayloadException(reasons.get(index));
      assertEquals("web log encrypted payload rejected: " + names.get(index), failure.getMessage());
      assertSame(reasons.get(index), failure.reason());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    var copy = WebLogPayloadException.Reason.values();
    copy[0] = WebLogPayloadException.Reason.PAYLOAD_INVALID;
    assertSame(WebLogPayloadException.Reason.KEY_UNAVAILABLE, WebLogPayloadException.Reason.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "key_unavailable", "KEY_UNAVAILABLE "))
      assertThrows(IllegalArgumentException.class, () -> WebLogPayloadException.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> WebLogPayloadException.Reason.valueOf(null));
  }
}
'''.replace('GOLDEN_HEX',golden.hex());s=s.replace('import static org.junit.jupiter.api.Assertions.*;', '\n'.join('import static org.junit.jupiter.api.Assertions.'+n+';' for n in ['assertArrayEquals','assertEquals','assertNotEquals','assertNotSame','assertNull','assertSame','assertThrows']));p.write_text(s);subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert sha(r/oldtest)==oldsha;out=b/'evidence/PG34660-web-log-value5-source-v1';out.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=4),dict(path=oldtest,tests=1)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r)),oldtest]},sdkHashes={},mainSourcesUnchanged=True,oldExceptionOneByteExact=True,oldTestSha256=oldsha,newDefinitions=4,necessaryPriorDefinitions=1,expectedTests=5,targets=['dev/codex/schubert/nk/web/logging/'+n for n in ['WebLogPayloadIdentity','EncryptedWebLogPayload','ClaimedWebLog','WebLogPayloadException','WebLogPayloadException$Reason']],independentAad=dict(spec='SS324352 eight length-prefixes 32bit BE/UUID BE; literal fields independent Python struct',fieldsHex=[v.hex() for v in fields],fieldLengths=[len(v) for v in fields],length=len(golden),goldenHex=golden.hex()),applicationTestsExecuted=0,newAcceptance=0,noWholeWebOrApiJarPayloadAccess=True);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=4,tests=5,newDefinitions=4,aadLength=len(golden),originalException1Unchanged=True)))
