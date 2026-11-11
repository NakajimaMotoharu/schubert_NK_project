"""Prepriced pure two-case BatchRun boundary manufacture; preserve original summary9 bytes."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26356-batch-run-boundary-manufacture-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());before=B/'evidence/PG26354-summary-helper-gap-before-v1/manifest.json';plan=load(before);assert plan['newNormalDefinitionsPlanned']==2 and plan['capPp']==2
summary=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/InspectionSummaryPortTest.java';current=load(B/'evidence/PG26348-summary-nine-unit-v1/begin.json');assert sha(summary)==current['inputHashes'][str(summary.relative_to(R))];pin=sha(summary)
test=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchRunBoundaryTest.java';assert not test.exists()
code='''package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-BAT-001; OPS-009; UI251; SS341 sections3/7; PT-BAT-RUN-BND001/002. */
final class BatchRunBoundaryTest {
  private static final UUID ID = new UUID(0, 1);

  @Test
  void literalTimestampExtremesAndRedactedDisplayAreAccepted() {
    // Independent PostgreSQL timestamp contract constants; no expected from the SUT.
    for (String literal : new String[] {"0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z"}) {
      Instant expected = Instant.parse(literal);
      BatchRun actual = new BatchRun(ID, expected);
      assertEquals(ID, actual.id());
      assertEquals(expected, actual.cutoff());
      assertEquals("BatchRun[identity/cutoff=<redacted>]", actual.toString());
    }
  }

  @Test
  void nullOutsideRangeAndSubMicrosecondInputsAreRejected() {
    Instant ordinary = Instant.parse("2026-11-05T00:00:00.123456Z");
    assertThrows(NullPointerException.class, () -> new BatchRun(null, ordinary));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
    // Three independent invalid causes: below min, above max, non-microsecond precision.
    for (String literal : new String[] {
      "0000-12-31T23:59:59.999999Z", "+10000-01-01T00:00:00Z", "2026-11-05T00:00:00.123456001Z"
    }) {
      Instant input = Instant.parse(literal);
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, input));
    }
  }
}
'''
java=R.parent/'toolchain/jdk-25.0.4/bin/java';formatter=R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar';cmd=[str(java),'-jar',str(formatter),'-'];v=subprocess.run(cmd,input=code.encode(),capture_output=True,timeout=30);assert v.returncode==0
again=subprocess.run(cmd,input=v.stdout,capture_output=True,timeout=30);assert again.returncode==0 and again.stdout==v.stdout
O.mkdir();(O/'formatter.stderr').write_bytes(v.stderr);test.write_bytes(v.stdout);assert sha(summary)==pin
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),beforeManifestSha256=sha(before),originalGroupEstimatePp=plan['originalGroupEstimatePp'],additionalSubworkEstimatePp=plan['additionalSubworkEstimatePp'],revisedGroupEstimatePp=plan['revisedGroupEstimatePp'],capPp=2,canonicalCostOwner=plan['canonicalCostOwner'],testPath=str(test.relative_to(R)),testSha256=sha(test),summaryWholeNineUnchangedSha256=pin,newTestDefinitions=2,normalExpectedCases=11,independentAcceptInputs=2,independentRejectInputs=5,MainSourcesChanged=False,productTestsExecuted=0,formatIdempotent=True,formatterSha256=sha(formatter),toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newDefinitions=2,old9Unchanged=True,mainChanged=False,manifestSha256=sha(O/'manifest.json'))))
