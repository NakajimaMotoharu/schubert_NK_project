"""Value-only reply and fixed exception assertions; no decoder, DLQ, process exit or backend."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/';names=['ValidatedReply','CommittedFatalReplyException','JmsContextFactory','package-info'];main=[base+n+'.java' for n in names];assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main);p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyValueContractTest.java';assert not p.exists();p.write_text('''package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-REPLY-VALUE001002; SS321: opaque value mechanics only, no validation/commit/exit proof. */
final class ReplyValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final String CAUSE_TEXT = "public unissued cause marker";

  @Test
  void replyvalue001OpaqueBytesRemainOwnedAndUuidAndJavaArrayValueContractsAreExact() {
    byte[] opaque = {1, 2, 3, 4};
    var value = new ValidatedReply(ID, opaque);
    opaque[0] = 9;
    assertEquals(ID, value.correlationId());
    byte[] first = value.body();
    assertArrayEquals(new byte[] {1, 2, 3, 4}, first);
    first[1] = 9;
    assertArrayEquals(new byte[] {1, 2, 3, 4}, value.body());
    assertNotSame(first, value.body());
    assertEquals(value, value);
    assertEquals("owned", Map.of(value, "owned").get(value));
    int stableHash = value.hashCode();
    value.body()[2] = 9;
    assertEquals(stableHash, value.hashCode());
    assertNotEquals(value, new ValidatedReply(ID, new byte[] {1, 2, 3, 4}));
    assertNotEquals(value, new ValidatedReply(new UUID(0, 2), new byte[] {1, 2, 3, 4}));
    assertNotEquals(value, null);
    assertNotEquals(value, CAUSE_TEXT);
    assertEquals("ValidatedReply[correlationId=00000000-0000-0000-0000-000000000001, body=<redacted>]", value.toString());
    assertThrows(NullPointerException.class, () -> new ValidatedReply(null, new byte[0]));
    assertThrows(NullPointerException.class, () -> new ValidatedReply(ID, null));
  }

  @Test
  void replyvalue002CommittedSignalRetainsExactCauseAndFixedPrimaryDiagnosticOnly() {
    for (Throwable cause : List.of(new IllegalStateException(CAUSE_TEXT), new AssertionError(CAUSE_TEXT))) {
      var value = new CommittedFatalReplyException(cause);
      assertSame(cause, value.getCause());
      assertEquals("invalid JMS reply was committed to the fatal DLQ", value.getMessage());
      assertEquals(0, value.getSuppressed().length);
      assertFalse(value.toString().contains(CAUSE_TEXT));
    }
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);prior=ld(b/'evidence/PG34844-ssc436-closed-namespace-source-inverse-v1/manifest.json');sdk={n:h for n,h in prior['sdkHashes'].items() if '/jakarta/jms/jakarta.jms-api/3.1.0/' in n};assert len(sdk)==1 and all(sha(Path(n))==h for n,h in sdk.items());out=b/'evidence/PG34940-reply-values-source-v1';out.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=2)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r))]},sdkHashes=sdk,mainSourcesUnchanged=True,newDefinitions=2,necessaryPriorDefinitions=0,expectedTests=2,expectedStaticNegatives=4,targets=['dev/codex/schubert/nk/web/messaging/'+n for n in names if n!='package-info'],valueFixtureOpaqueOnly=True,protocolValidationOrDurableCommitOrProcessExitQualified=False,noWholeWebOrApiJarPayloadAccess=True,applicationTestsExecuted=0,newAcceptance=0);(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=len(main),tests=v['expectedTests'],staticNegatives=v['expectedStaticNegatives'],SDK=len(sdk))))
