"""New independent value/time/count/address/retry fixtures, no persistence, provider or JMS action."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base='src/schubert-nk-api/src/';q='java/dev/codex/schubert/nk/api/application/question/';o='java/dev/codex/schubert/nk/api/messaging/outbound/';mains=[base+'main/'+q+n+'.java' for n in ['QuestionCommandMetadata','AnswerResult']]+[base+'main/'+o+n+'.java' for n in ['OutboxDispatchReport','OutboxDestination','OutboxRetrySchedule']];old=[dict(path=base+'test/'+q+'QuestionCommandMetadataContractTest.java',tests=2),dict(path=base+'test/'+o+'OutboxDispatchReportBoundaryTest.java',tests=3)];assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in mains+[x['path'] for x in old]);fixtures={base+'test/'+q+'QuestionValueContractTest.java':'''package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-CMD-VALUE001..003; SS312/332/351/354: provider result is never persisted completion. */
final class QuestionValueContractTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);
  private static final String BODY = "PUBLIC_ANSWER\\ne\\u0301";

  @Test
  void value001UtcYearAndMicrosecondGoldenBoundsPreserveTraceAndTruncateBeforeRangeCheck() {
    String[][] vectors = {
      {"0001-01-01T00:00:00Z", "0001-01-01T00:00:00Z"},
      {"9999-12-31T23:59:59.999999999Z", "9999-12-31T23:59:59.999999Z"},
      {"2024-01-01T00:00:00.123456789Z", "2024-01-01T00:00:00.123456Z"},
      {"1969-12-31T23:59:59.999999999Z", "1969-12-31T23:59:59.999999Z"}
    };
    for (String[] vector : vectors) {
      QuestionCommandMetadata value =
          new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.parse(vector[0]));
      assertEquals(Instant.parse(vector[1]), value.at());
      assertEquals(MESSAGE, value.messageId());
      assertEquals(CORRELATION, value.correlationId());
      assertEquals("QuestionCommandMetadata[REDACTED]", value.toString());
    }
    for (String outside :
        List.of("0000-12-31T23:59:59.999999999Z", "+10000-01-01T00:00:00Z")) {
      Instant at = Instant.parse(outside);
      assertEquals(
          "command time is outside UTC range",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new QuestionCommandMetadata(MESSAGE, CORRELATION, at))
              .getMessage());
    }
  }

  @Test
  void value002EveryTraceComponentDefinesValueIdentityAfterCanonicalMicrosecondTruncation() {
    QuestionCommandMetadata value = new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.EPOCH);
    sameValue(
        value,
        new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.parse("1970-01-01T00:00:00.000000999Z")),
        List.of(
            new QuestionCommandMetadata(CORRELATION, CORRELATION, Instant.EPOCH),
            new QuestionCommandMetadata(MESSAGE, MESSAGE, Instant.EPOCH),
            new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.parse("1970-01-01T00:00:00.000001Z"))));
  }

  @Test
  void value003ProviderAnswerRetainsExactBodyAndTimeWithClosedRenderingAndNonnullComponents() {
    Instant at = Instant.parse("2024-01-01T00:00:00.123456789Z");
    AnswerResult value = new AnswerResult(BODY, at);
    assertEquals(BODY, value.body());
    assertEquals(at, value.answeredAt());
    assertEquals("AnswerResult[REDACTED]", value.toString());
    assertEquals("", new AnswerResult("", Instant.EPOCH).body());
    sameValue(value, new AnswerResult(BODY, at), List.of(new AnswerResult("other", at), new AnswerResult(BODY, Instant.EPOCH)));
    assertEquals("answer body", assertThrows(NullPointerException.class, () -> new AnswerResult(null, at)).getMessage());
    assertEquals("answer time", assertThrows(NullPointerException.class, () -> new AnswerResult(BODY, null)).getMessage());
  }

  private static <T> void sameValue(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
''',base+'test/'+o+'OutboxValueContractTest.java':'''package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-OUTBOX-VALUE001..003; SS324/332 application-Outbox, no send/lease/DB or WebLog schedule. */
final class OutboxValueContractTest {
  @Test
  void value001ReportEqualityRetainsEveryConsistentCountAndOrdinaryPublicRendering() {
    OutboxDispatchReport value = new OutboxDispatchReport(3, 1, 1, 1);
    OutboxDispatchReport equal = new OutboxDispatchReport(3, 1, 1, 1);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (OutboxDispatchReport other :
        List.of(new OutboxDispatchReport(4, 2, 1, 1), new OutboxDispatchReport(3, 0, 2, 1), new OutboxDispatchReport(3, 1, 0, 2))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
    assertEquals("OutboxDispatchReport[claimed=3, sent=1, failed=1, leaseLost=1]", value.toString());
  }

  @Test
  void value002DestinationKeepsExactlyTwoFixedAddressesAndDefensiveClosedEnumFactories() {
    String[] names = {"ASYNC_WORK", "DLQ"};
    String[] addresses = {"nk.async.work", "nk.dead.letter"};
    OutboxDestination[] values = OutboxDestination.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, values[i].ordinal());
      assertEquals(addresses[i], values[i].address());
      assertSame(values[i], OutboxDestination.valueOf(names[i]));
      assertSame(values[i], OutboxDestination.fromAddress(addresses[i]));
    }
    OutboxDestination[] copy = OutboxDestination.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(OutboxDestination.ASYNC_WORK, OutboxDestination.values()[0]);
    for (String unknown : List.of("", "NK.ASYNC.WORK", "nk.async.work ", "unknown")) {
      IllegalArgumentException failure = assertThrows(IllegalArgumentException.class, () -> OutboxDestination.fromAddress(unknown));
      assertEquals("outbox destination is not allowed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    assertEquals("address", assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null)).getMessage());
    assertThrows(IllegalArgumentException.class, () -> OutboxDestination.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> OutboxDestination.valueOf(null));
  }

  @Test
  void value003ApplicationRetryUsesIndependentFiveByThreeGoldenOffsetsAndAllHundredAttempts() {
    OutboxRetrySchedule schedule = OutboxRetrySchedule.INSTANCE;
    assertArrayEquals(new String[] {"INSTANCE"}, Arrays.stream(OutboxRetrySchedule.values()).map(Enum::name).toArray(String[]::new));
    assertSame(schedule, OutboxRetrySchedule.valueOf("INSTANCE"));
    assertThrows(IllegalArgumentException.class, () -> OutboxRetrySchedule.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> OutboxRetrySchedule.valueOf(null));
    OutboxRetrySchedule[] copy = OutboxRetrySchedule.values();
    assertNotSame(copy, OutboxRetrySchedule.values());
    copy[0] = null;
    assertSame(schedule, OutboxRetrySchedule.values()[0]);
    long[] bases = {1000, 5000, 30000, 60000, 300000};
    long[][] offsets = {{900, 1000, 1100}, {4500, 5000, 5500}, {27000, 30000, 33000}, {54000, 60000, 66000}, {270000, 300000, 330000}};
    int[] jitters = {-100, 0, 100};
    for (int attempt = 1; attempt <= 100; attempt++) {
      int row = Math.min(attempt - 1, 4);
      assertEquals(Duration.ofMillis(bases[row]), schedule.delayAfterFailure(attempt));
      for (int i = 0; i < jitters.length; i++) {
        assertEquals(Instant.ofEpochMilli(offsets[row][i]), schedule.nextAttemptAt(Instant.EPOCH, attempt, jitters[i]));
      }
    }
    for (int invalid : new int[] {Integer.MIN_VALUE, -1, 0, 101, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> schedule.delayAfterFailure(invalid));
      assertThrows(IllegalArgumentException.class, () -> schedule.nextAttemptAt(Instant.EPOCH, invalid, 0));
    }
    for (int invalid : new int[] {Integer.MIN_VALUE, -101, 101, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> schedule.nextAttemptAt(Instant.EPOCH, 1, invalid));
    }
    assertThrows(NullPointerException.class, () -> schedule.nextAttemptAt(null, 1, 0));
    assertThrows(DateTimeException.class, () -> schedule.nextAttemptAt(Instant.MAX, 1, 0));
  }
}
'''}
fmt=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];new=[]
for n,text in fixtures.items():
 p=r/n;assert not p.exists();p.open('x').write(text);subprocess.run(fmt+['--replace',str(p)],check=True,timeout=30);new.append(dict(path=n,tests=3))
tests=old+new;inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={n:next(x for x in inv['artifacts'] if x['path']==n)['owner'] for n in mains};targets=[n.split('/main/java/')[1].removesuffix('.java') for n in mains];e=b/'evidence/PG35350-api-command-outbox11-source-v1';e.mkdir();v=dict(actualExit=0,mainSources=mains,testSources=tests,expectedTests=11,newTestDefinitions=6,necessaryPriorDefinitions=5,inputHashes={n:sha(r/n) for n in mains+[x['path'] for x in tests]},unchangedMainAndOriginalMetadataTwoReportThree=True,productOwnerByMainPath=owners,targets=targets,applicationOutboxPolicyDistinctFromWebLogQa050=True,actualBackendJmsProviderOrAuthorityActions=0);(e/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');c=ld(b/'input/4073_storage_lexical6_profile_v2.json');c.update(id='PG35360-API-COMMAND-OUTBOX-PURE11',productOwnerByMainPath=owners,oracleSpecs=[ref(b/'4381_API質問値・Outbox純値全十一仕様.md')],closureProofs=[ref(e/'manifest.json')],mainSources=mains,testSources=tests,expectedTests=11,newTestDefinitions=6,physicalClasses=[n+'.class' for n in targets],targetClasses=targets,pomInputs=['pom.xml','src/schubert-nk-api/pom.xml'],slots={k:str((b/('evidence/PG'+str(n)+'-api-command-outbox11-'+k+'-v1')).relative_to(r)) for k,n in [('prestyle',35352),('prepare',35354),('static',35356),('preflight',35358),('unit',35360),('post',35362)]},privateDirs=dict(prepare='pg35354-api-command-outbox11-v1',unit='pg35360-api-command-outbox11-v1'));(b/'input/4085_api_command_outbox11_profile.json').open('x').write(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=5,tests=11,newDefinitions=6,originalFiveUnchanged=True,owners=owners)))
