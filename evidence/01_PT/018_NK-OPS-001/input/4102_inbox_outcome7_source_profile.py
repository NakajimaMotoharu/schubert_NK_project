"""Independent eight-Code-class Inbox outcome data profile, never old DB fixture or actual crypto."""
from pathlib import Path
p=Path('/home/mini/codex/project1/work/pgpt-foundation/src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/InboxOutcomeValueContractTest.java');assert not p.exists();p.open('x').write('''package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-IDEM-OUTCOME001..004; SS324/331/352/354: inert data, never crypto/DB/session authority. */
final class InboxOutcomeValueContractTest {
  private static final String KEY_VERSION = "v1";
  private static final String LAYOUT = "QRYRSP01";
  private static final String VERSION = "001";
  private static final UUID ID = new UUID(0, 1);
  private static final UUID OTHER_ID = new UUID(0, 2);

  @Test
  void outcome001SyntheticCiphertextMetadataKeepsLengthBoundsAndCallerIsolationWithoutCrypto() {
    byte[] expected = new byte[29];
    Arrays.fill(expected, (byte) 7);
    byte[] input = expected.clone();
    EncryptedResponseSnapshot value = new EncryptedResponseSnapshot(KEY_VERSION, input);
    byte[] exported = value.ciphertext();
    assertNotSame(input, exported);
    assertArrayEquals(expected, exported);
    Map<EncryptedResponseSnapshot, String> retained = Map.of(value, "retained");
    int hashBefore = value.hashCode();
    input[0] = 99;
    exported[1] = 88;
    assertArrayEquals(expected, value.ciphertext());
    assertEquals("retained", retained.get(value));
    assertEquals(hashBefore, value.hashCode());
    assertEquals(KEY_VERSION, value.keyVersion());
    assertEquals("EncryptedResponseSnapshot[keyVersion=v1, ciphertext=<redacted>]", value.toString());
    assertEquals(value, value);
    assertNotEquals(value, null);
    assertNotEquals(value, VERSION);
    assertNotEquals(value, new EncryptedResponseSnapshot("v2", expected));
    assertNotEquals(value, new EncryptedResponseSnapshot(KEY_VERSION, new byte[30]));
    for (String version : List.of("a", "1", "V1", "a".repeat(16))) {
      assertEquals(version, new EncryptedResponseSnapshot(version, expected).keyVersion());
    }
    assertEquals(1_050_000, new EncryptedResponseSnapshot(KEY_VERSION, new byte[1_050_000]).ciphertext().length);
    for (String invalid : List.of("", "_v", "v/a", "a".repeat(17), "v\\n", "あ")) {
      assertEquals("response snapshot key version is invalid", assertThrows(IllegalArgumentException.class, () -> new EncryptedResponseSnapshot(invalid, expected)).getMessage());
    }
    for (int invalid : new int[] {0, 28, 1_050_001}) {
      byte[] bytes = new byte[invalid];
      assertEquals("response snapshot ciphertext length is invalid", assertThrows(IllegalArgumentException.class, () -> new EncryptedResponseSnapshot(KEY_VERSION, bytes)).getMessage());
    }
    assertThrows(NullPointerException.class, () -> new EncryptedResponseSnapshot(null, expected));
    assertThrows(NullPointerException.class, () -> new EncryptedResponseSnapshot(KEY_VERSION, null));
  }

  @Test
  void outcome002CompletionLexicalMetadataAndAllSixComponentsKeepTheirPublicValueContract() {
    String[] stateNames = {"COMPLETED", "ERROR"};
    InboxCompletionState[] states = InboxCompletionState.values();
    assertArrayEquals(stateNames, Arrays.stream(states).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < states.length; i++) {
      InboxCompletionState state = states[i];
      assertEquals(i, state.ordinal());
      assertSame(state, InboxCompletionState.valueOf(stateNames[i]));
      for (String layout : List.of(LAYOUT, "00000000", "Z9Z9Z9Z9")) {
        for (String version : List.of("000", VERSION, "999")) {
          InboxCompletion actual = new InboxCompletion(state, InboxResultReference.none(), layout, version, Optional.empty(), Instant.EPOCH);
          assertSame(state, actual.state());
          assertEquals(InboxResultReference.none(), actual.resultReference());
          assertEquals(layout, actual.responseLayoutId());
          assertEquals(version, actual.responseVersion());
          assertEquals(Optional.empty(), actual.responseSnapshot());
          assertEquals(Instant.EPOCH, actual.completedAt());
          assertEquals("InboxCompletion[state=" + stateNames[i] + ", response metadata/result=<redacted>]", actual.toString());
        }
      }
    }
    InboxCompletionState[] copy = InboxCompletionState.values();
    assertNotSame(states, copy);
    copy[0] = null;
    assertSame(InboxCompletionState.COMPLETED, InboxCompletionState.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> InboxCompletionState.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> InboxCompletionState.valueOf(null));
    for (String bad : List.of("", "ABC", "abc12345", "ABC123456", "ABC1234_", "ABC1234\\n")) {
      assertEquals("responseLayoutId is invalid", assertThrows(IllegalArgumentException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), bad, VERSION, Optional.empty(), Instant.EPOCH)).getMessage());
    }
    for (String bad : List.of("", "01", "0000", "a01", "0 1", "00\\n")) {
      assertEquals("responseVersion is invalid", assertThrows(IllegalArgumentException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, bad, Optional.empty(), Instant.EPOCH)).getMessage());
    }
    assertThrows(NullPointerException.class, () -> new InboxCompletion(null, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, null, LAYOUT, VERSION, Optional.empty(), Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), null, VERSION, Optional.empty(), Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, null, Optional.empty(), Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, VERSION, null, Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), null));
    EncryptedResponseSnapshot payload = new EncryptedResponseSnapshot(KEY_VERSION, new byte[29]);
    InboxCompletion withPayload = new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, VERSION, Optional.of(payload), Instant.EPOCH);
    assertSame(payload, withPayload.responseSnapshot().orElseThrow());
    sameValue(completed(), completed(), List.of(
        new InboxCompletion(InboxCompletionState.ERROR, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH),
        new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.numeric(InboxResultReferenceType.USER, 1), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH),
        new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), "NTFRSP01", VERSION, Optional.empty(), Instant.EPOCH),
        new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, "002", Optional.empty(), Instant.EPOCH),
        withPayload,
        new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH.plusSeconds(1))));
  }

  @Test
  void outcome003SixStatusPresenceCellsAndFactoriesKeepTerminalDataSeparateFromInProgress() {
    String[] names = {"EXECUTED", "REPLAY", "IN_PROGRESS"};
    InboxExecutionStatus[] statuses = InboxExecutionStatus.values();
    assertArrayEquals(names, Arrays.stream(statuses).map(Enum::name).toArray(String[]::new));
    Set<String> accepted = Set.of("EXECUTED:true", "REPLAY:true", "IN_PROGRESS:false");
    InboxCompletion completion = completed();
    int allowed = 0;
    int rejected = 0;
    for (int i = 0; i < statuses.length; i++) {
      InboxExecutionStatus status = statuses[i];
      assertEquals(i, status.ordinal());
      assertSame(status, InboxExecutionStatus.valueOf(names[i]));
      for (boolean present : List.of(false, true)) {
        Optional<InboxCompletion> optional = present ? Optional.of(completion) : Optional.empty();
        if (accepted.contains(names[i] + ":" + present)) {
          InboxExecution actual = new InboxExecution(status, optional);
          assertSame(status, actual.status());
          assertEquals(optional, actual.completion());
          assertEquals("InboxExecution[status=" + names[i] + ", completion=<redacted>]", actual.toString());
          allowed++;
        } else {
          IllegalArgumentException failure = assertThrows(IllegalArgumentException.class, () -> new InboxExecution(status, optional));
          assertEquals("Inbox outcome and completion presence do not match", failure.getMessage());
          assertNull(failure.getCause());
          rejected++;
        }
      }
    }
    assertEquals(3, allowed);
    assertEquals(3, rejected);
    InboxExecutionStatus[] copy = InboxExecutionStatus.values();
    assertNotSame(statuses, copy);
    copy[0] = null;
    assertSame(InboxExecutionStatus.EXECUTED, InboxExecutionStatus.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> InboxExecutionStatus.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> InboxExecutionStatus.valueOf(null));
    assertSame(completion, InboxExecution.executed(completion).completion().orElseThrow());
    assertSame(completion, InboxExecution.replay(completion).completion().orElseThrow());
    assertSame(InboxExecutionStatus.EXECUTED, InboxExecution.executed(completion).status());
    assertSame(InboxExecutionStatus.REPLAY, InboxExecution.replay(completion).status());
    assertSame(InboxExecutionStatus.IN_PROGRESS, InboxExecution.inProgress().status());
    assertEquals(Optional.empty(), InboxExecution.inProgress().completion());
    assertThrows(NullPointerException.class, () -> new InboxExecution(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new InboxExecution(InboxExecutionStatus.IN_PROGRESS, null));
    assertThrows(NullPointerException.class, () -> InboxExecution.executed(null));
    assertThrows(NullPointerException.class, () -> InboxExecution.replay(null));
    InboxCompletion other = new InboxCompletion(InboxCompletionState.ERROR, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH);
    sameValue(InboxExecution.executed(completion), InboxExecution.executed(completed()), List.of(InboxExecution.replay(completion), InboxExecution.inProgress(), InboxExecution.executed(other)));
    sameValue(InboxExecution.inProgress(), InboxExecution.inProgress(), List.of(InboxExecution.executed(completion)));
  }

  @Test
  void outcome004BoundSourceIdentityIsInertRequiredDataWithTwoComponentValueSemantics() {
    InboxExecution execution = InboxExecution.inProgress();
    BoundInboxExecution value = new BoundInboxExecution(ID, execution);
    assertEquals(ID, value.sourceMessageId());
    assertSame(execution, value.execution());
    assertEquals("BoundInboxExecution[REDACTED]", value.toString());
    sameValue(value, new BoundInboxExecution(ID, InboxExecution.inProgress()), List.of(new BoundInboxExecution(OTHER_ID, execution), new BoundInboxExecution(ID, InboxExecution.executed(completed()))));
    assertThrows(NullPointerException.class, () -> new BoundInboxExecution(null, execution));
    assertThrows(NullPointerException.class, () -> new BoundInboxExecution(ID, null));
  }

  private static InboxCompletion completed() {
    return new InboxCompletion(InboxCompletionState.COMPLETED, InboxResultReference.none(), LAYOUT, VERSION, Optional.empty(), Instant.EPOCH);
  }

  private static <T> void sameValue(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, VERSION);
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
''')

import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/';names=['InboxResultReference','InboxResultReferenceType','EncryptedResponseSnapshot','InboxCompletionState','InboxCompletion','InboxExecutionStatus','InboxExecution','BoundInboxExecution'];mains=[prefix+n+'.java' for n in names];old='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/InboxReferenceValueContractTest.java';assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in mains+[old]);prior=ld(b/'evidence/PG35380-inbox-reference3-source-v1/manifest.json');assert all(sha(r/n)==h for n,h in prior['inputHashes'].items());subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);new=str(p.relative_to(r));tests=[dict(path=old,tests=3),dict(path=new,tests=4)];inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={n:next(x for x in inv['artifacts'] if x['path']==n)['owner'] for n in mains};targets=[n.split('/main/java/')[1].removesuffix('.java') for n in mains];e=b/'evidence/PG35400-inbox-outcome7-source-v1';e.mkdir();v=dict(actualExit=0,mainSources=mains,testSources=tests,expectedTests=7,newTestDefinitions=4,necessaryPriorDefinitions=3,inputHashes={n:sha(r/n) for n in mains+[old,new]},unchangedMainAndOriginalReferenceThree=True,newSixMainDependentClosureRequiresSameRunReferenceThree=True,originalDbBoundFixtureExtractedOrCompiled=False,actualCryptoCodecKeyringDbOrAuthorityActions=0,ciphertextInertSyntheticOnly=True,productOwnerByMainPath=owners,targets=targets);(e/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');c=ld(b/'input/4094_inbox_reference3_profile.json');c.update(id='PG35410-INBOX-OUTCOME-PURE7',productOwnerByMainPath=owners,oracleSpecs=[ref(b/'4385_Inbox結果純値八class・通常七仕様.md'),ref(b/'4383_Inbox参照純値・独立八十四cell全三仕様.md')],closureProofs=[ref(e/'manifest.json')],mainSources=mains,testSources=tests,expectedTests=7,newTestDefinitions=4,physicalClasses=[n+'.class' for n in targets],targetClasses=targets,slots={k:str((b/('evidence/PG'+str(n)+'-inbox-outcome7-'+k+'-v1')).relative_to(r)) for k,n in [('prestyle',35402),('prepare',35404),('static',35406),('preflight',35408),('unit',35410),('post',35412)]},privateDirs=dict(prepare='pg35404-inbox-outcome7-v1',unit='pg35410-inbox-outcome7-v1'));(b/'input/4103_inbox_outcome7_profile.json').open('x').write(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=8,tests=7,newDefinitions=4,necessaryPriorDefinitions=3,owners=owners)))
