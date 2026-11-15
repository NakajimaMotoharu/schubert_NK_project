package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BATRUN-VALUE001; SS331/341/354 SSC440: data only, never a real run/owner/boot grant. */
final class BatchRunPureContractTest {
  @Test
  void runValue001RequiredIdentityExactUtcMicrosecondsAndRecordValueAreIndependent() {
    UUID id = new UUID(0, 1);
    UUID otherId = new UUID(0, 2);
    for (String valid :
        List.of(
            "0001-01-01T00:00:00Z", "1970-01-01T00:00:00.000001Z", "9999-12-31T23:59:59.999999Z")) {
      Instant at = Instant.parse(valid);
      BatchRun run = new BatchRun(id, at);
      assertEquals(id, run.id());
      assertEquals(at, run.cutoff());
      assertEquals("BatchRun[identity/cutoff=<redacted>]", run.toString());
    }
    for (Instant invalid :
        List.of(
            Instant.MIN, Instant.MAX, Instant.EPOCH.plusNanos(1), Instant.EPOCH.minusNanos(1))) {
      assertEquals(
          "batch cutoff is outside the timestamp contract",
          assertThrows(IllegalArgumentException.class, () -> new BatchRun(id, invalid))
              .getMessage());
    }
    assertThrows(NullPointerException.class, () -> new BatchRun(null, Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> new BatchRun(id, null));
    BatchRun value = new BatchRun(id, Instant.EPOCH);
    BatchRun equal = new BatchRun(id, Instant.EPOCH);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (BatchRun other :
        List.of(
            new BatchRun(otherId, Instant.EPOCH),
            new BatchRun(id, Instant.EPOCH.plusNanos(1000)))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
