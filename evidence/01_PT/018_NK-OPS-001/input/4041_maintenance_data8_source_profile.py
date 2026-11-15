"""Pure immutable metadata only; no actual completion, retirement, IO, authority or held fixture."""
from pathlib import Path
import datetime,hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));base='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/';names=['BatchRun','MaintenanceActivation','MaintenanceCompletion','MaintenanceRunState','MaintenanceRetirement'];main=[base+n+'.java' for n in names];tb='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/';old=tb+'MaintenanceRunStateValuesTest.java';assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[old]);test=tb+'MaintenanceDataValueContractTest.java';p=r/test;assert not p.exists();p.write_text('''package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-MVALUE001002; SS331/341/343: immutable public data only, never operational permission. */
final class MaintenanceDataValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final UUID OTHER_ID = new UUID(0, 2);
  private static final Instant CUTOFF = Instant.parse("2024-01-01T00:00:00Z");
  private static final Instant END = Instant.parse("2024-01-02T00:00:00Z");
  private static final Instant PREPARED = Instant.parse("2025-02-06T00:00:00Z");
  private static final Instant AGE400 = Instant.parse("2025-02-05T00:00:00Z");
  private static final BatchRun RUN = new BatchRun(ID, CUTOFF);
  private static final MaintenanceActivation ACTIVE = new MaintenanceActivation(RUN, ID);
  private static final String HASH = "a".repeat(64);
  private static final String OTHER_HASH = "f".repeat(64);
  private static final String UNKNOWN = "PUBLIC_UNKNOWN";

  private static <T> void values(T actual, T equal, List<T> different) {
    assertEquals(actual, actual); assertEquals(actual, equal); assertEquals(equal, actual);
    assertEquals(actual.hashCode(), equal.hashCode()); assertEquals("found", Map.of(actual, "found").get(equal));
    assertNotEquals(actual, null); assertNotEquals(actual, UNKNOWN);
    for (T other : different) { assertNotEquals(actual, other); assertNotEquals(other, actual); }
  }

  @Test
  void mvalue001RunActivationCompletionAndStateKeepAllComponentsAndClosedOutcome() {
    values(RUN, new BatchRun(ID, CUTOFF), List.of(new BatchRun(OTHER_ID, CUTOFF), new BatchRun(ID, CUTOFF.plusNanos(1000))));
    assertEquals(ID, RUN.id()); assertEquals(CUTOFF, RUN.cutoff());
    assertEquals("BatchRun[identity/cutoff=<redacted>]", RUN.toString());
    for (String valid : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      Instant at = Instant.parse(valid); assertEquals(at, new BatchRun(ID, at).cutoff());
    }
    for (String invalid : List.of("0000-12-31T23:59:59.999999Z", "+10000-01-01T00:00:00Z", "2024-01-01T00:00:00.000000001Z")) {
      Instant at = Instant.parse(invalid); assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, at));
    }
    assertThrows(NullPointerException.class, () -> new BatchRun(null, CUTOFF));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
    values(ACTIVE, new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID),
        List.of(new MaintenanceActivation(new BatchRun(OTHER_ID, CUTOFF), ID), new MaintenanceActivation(RUN, OTHER_ID)));
    assertSame(RUN, ACTIVE.run()); assertEquals(ID, ACTIVE.id());
    assertEquals(LocalDate.of(2024, 1, 1), ACTIVE.businessDate());
    assertEquals(LocalDate.of(2026, 9, 13), new MaintenanceActivation(new BatchRun(ID, Instant.parse("2026-09-12T15:00:00Z")), ID).businessDate());
    assertEquals("MaintenanceActivation[identity/cutoff=<redacted>]", ACTIVE.toString());
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(null, ID));
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(RUN, null));
    var completed = new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.SUCCESS);
    values(completed, new MaintenanceCompletion(new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID), END, MaintenanceCompletion.Outcome.SUCCESS),
        List.of(new MaintenanceCompletion(new MaintenanceActivation(RUN, OTHER_ID), END, MaintenanceCompletion.Outcome.SUCCESS),
            new MaintenanceCompletion(ACTIVE, END.plusNanos(1000), MaintenanceCompletion.Outcome.SUCCESS),
            new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.WARNING)));
    var pending = new MaintenanceRunState(ACTIVE, Optional.empty());
    values(pending, new MaintenanceRunState(new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID), Optional.empty()),
        List.of(new MaintenanceRunState(new MaintenanceActivation(RUN, OTHER_ID), Optional.empty()), new MaintenanceRunState(ACTIVE, Optional.of(completed))));
    var doneData = new MaintenanceRunState(ACTIVE, Optional.of(completed));
    values(doneData, new MaintenanceRunState(ACTIVE, Optional.of(new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.SUCCESS))),
        List.of(new MaintenanceRunState(ACTIVE, Optional.of(new MaintenanceCompletion(ACTIVE, END.plusNanos(1000), MaintenanceCompletion.Outcome.SUCCESS)))));
    assertSame(ACTIVE, doneData.activation()); assertSame(completed, doneData.completion().orElseThrow());
    assertEquals("MaintenanceRunState[redacted]", doneData.toString());
    assertArrayEquals(new String[] {"SUCCESS", "WARNING"}, Arrays.stream(MaintenanceCompletion.Outcome.values()).map(Enum::name).toArray(String[]::new));
    assertSame(MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.valueOf("SUCCESS"));
    assertSame(MaintenanceCompletion.Outcome.WARNING, MaintenanceCompletion.Outcome.valueOf("WARNING"));
    var outcomes = MaintenanceCompletion.Outcome.values(); outcomes[0] = MaintenanceCompletion.Outcome.WARNING;
    assertSame(MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.values()[0]);
    assertEquals(0, MaintenanceCompletion.Outcome.SUCCESS.exitCode()); assertEquals(10, MaintenanceCompletion.Outcome.WARNING.exitCode());
    for (String invalid : List.of("", "success", UNKNOWN)) assertThrows(IllegalArgumentException.class, () -> MaintenanceCompletion.Outcome.valueOf(invalid));
    assertThrows(NullPointerException.class, () -> MaintenanceCompletion.Outcome.valueOf(null));
  }

  @Test
  void mvalue002RetirementDataStrictAgePrecisionCountDigestAndValueBoundsAreIndependent() {
    var actual = new MaintenanceRetirement(RUN, END, PREPARED, 1, HASH);
    values(actual, new MaintenanceRetirement(new BatchRun(ID, CUTOFF), END, PREPARED, 1, HASH),
        List.of(new MaintenanceRetirement(new BatchRun(OTHER_ID, CUTOFF), END, PREPARED, 1, HASH),
            new MaintenanceRetirement(RUN, END.plusNanos(1000), PREPARED, 1, HASH),
            new MaintenanceRetirement(RUN, END, PREPARED.plusNanos(1000), 1, HASH),
            new MaintenanceRetirement(RUN, END, PREPARED, 2, HASH), new MaintenanceRetirement(RUN, END, PREPARED, 1, OTHER_HASH)));
    assertSame(RUN, actual.run()); assertEquals(END, actual.latestEnded()); assertEquals(PREPARED, actual.preparedAt());
    assertEquals(1, actual.count()); assertEquals(HASH, actual.digest());
    assertEquals("MaintenanceRetirement[identity/time/plan=<redacted>]", actual.toString());
    for (int count : List.of(1, Integer.MAX_VALUE))
      for (String hash : List.of("0".repeat(64), OTHER_HASH)) {
        var valid = new MaintenanceRetirement(RUN, END, AGE400.plusNanos(1000), count, hash);
        assertEquals(count, valid.count()); assertEquals(hash, valid.digest());
        assertEquals(Instant.parse("2025-02-05T00:00:00.000001Z"), valid.preparedAt());
      }
    Instant maximum = Instant.parse("9999-12-31T23:59:59.999999Z");
    assertEquals(maximum, new MaintenanceRetirement(RUN, END, maximum, 1, HASH).preparedAt());
    for (Instant latest : List.of(CUTOFF.minusNanos(1000), Instant.parse("+10000-01-01T00:00:00Z"), END.plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> new MaintenanceRetirement(RUN, latest, PREPARED, 1, HASH));
    for (Instant prepared : List.of(Instant.parse("+10000-01-01T00:00:00Z"), PREPARED.plusNanos(1), AGE400, AGE400.minusNanos(1000), END.minusNanos(1000)))
      assertThrows(IllegalArgumentException.class, () -> new MaintenanceRetirement(RUN, END, prepared, 1, HASH));
    for (int count : List.of(Integer.MIN_VALUE, -1, 0)) assertThrows(IllegalArgumentException.class, () -> new MaintenanceRetirement(RUN, END, PREPARED, count, HASH));
    for (String hash : List.of("", "a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64), " " + HASH, HASH + "\\n"))
      assertThrows(IllegalArgumentException.class, () -> new MaintenanceRetirement(RUN, END, PREPARED, 1, hash));
    assertThrows(NullPointerException.class, () -> new MaintenanceRetirement(null, END, PREPARED, 1, HASH));
    assertThrows(NullPointerException.class, () -> new MaintenanceRetirement(RUN, null, PREPARED, 1, HASH));
    assertThrows(NullPointerException.class, () -> new MaintenanceRetirement(RUN, END, null, 1, HASH));
    assertThrows(NullPointerException.class, () -> new MaintenanceRetirement(RUN, END, PREPARED, 1, null));
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[old]);assert datetime.datetime(2024,1,2,tzinfo=datetime.timezone.utc)+datetime.timedelta(days=400)==datetime.datetime(2025,2,5,tzinfo=datetime.timezone.utc)
inv=json.loads((r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text());owners={n:next(x['owner'] for x in inv['artifacts'] if x['path']==n) for n in main};physical=['dev/codex/schubert/nk/batch/repository/'+n+'.class' for n in names]+['dev/codex/schubert/nk/batch/repository/MaintenanceCompletion$Outcome.class']
for n in main+[old,test]:
 text=(r/n).read_text();assert not any(word in text for word in ['java.nio.file','java.sql','java.net','ProcessBuilder','System.exit','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
for n in physical:policy.relative_name(n)
o=b/'evidence/PG35200-maintenance-data8-source-closure-v1';o.mkdir();v=dict(actualExit=0,inputHashes={n:sha(r/n) for n in main+[old,test]},mainSources=main,testSources=[dict(path=old,tests=6),dict(path=test,tests=2)],owners=owners,physicalClasses=physical,mainSourcesUnchanged=True,originalRunState6ByteExact=True,newDefinitions=2,necessaryPriorDefinitions=6,expectedTests=8,independentAge400Golden=dict(fromUTC='2024-01-02T00:00:00Z',strict400DaysUTC='2025-02-05T00:00:00Z',firstAllowedMicrosecondUTC='2025-02-05T00:00:00.000001Z',independentCalculator='Python datetime.timedelta not Java production code'),sourceImportsAndBodiesClosedJdkValuesOnly=True,dataConstructorIsNotOperationalPermission=True,applicationTestsExecuted=0,newAcceptance=0);(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
cfg=dict(schema='PGPT_CLOSED_HOST_PROFILE_V1',id='PG35210-MAINTENANCE-DATA-WHOLE8',costWbsLeafIds=['WBS-F03'],costBoundary='ADDITIONAL_QUALIFICATION_NO_ORIGINAL_COST_REASSIGNMENT',productOwnerByMainPath=owners,oracleSpecs=[ref(b/'4371_Maintenance純値六class・通常八仕様.md')],closureProofs=[ref(o/'manifest.json')],qualityExceptions=[],coverageExclusions=[],productionCoreMain='deaed367cb4f234af95fe9e96014f6c01e30486d',mainSources=main,testSources=v['testSources'],expectedTests=8,newTestDefinitions=2,resources=[],sdkJars=[],preparedDependencyHashes={str(x):sha(x) for x in [policy.ANN,policy.CONSOLE]},physicalClasses=physical,targetClasses=[n[:-6] for n in physical],pomInputs=['pom.xml','src/schubert-nk-batch/pom.xml'],systemProperties={},slots={n:str((b/('evidence/PG'+str(i)+'-maintenance-data8-'+n+'-v1')).relative_to(r)) for n,i in [('prestyle',35202),('prepare',35204),('static',35206),('preflight',35208),('unit',35210),('post',35212)]},privateDirs=dict(prepare='pg35204-maintenance-data8-v1',unit='pg35210-maintenance-data8-v1'));policy.validate_syntax(cfg);(b/'input/4042_maintenance_data8_profile.json').open('x').write(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=5,physical=6,wholeTests=8,newDefinitions=2,original6ByteExact=True,unneededProtocolPayload=0)))
