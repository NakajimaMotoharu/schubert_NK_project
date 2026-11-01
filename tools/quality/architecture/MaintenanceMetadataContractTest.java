package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.StorageIdentity;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Plain metadata only; no filesystem identity lookup, run file, DB or parent gate. */
final class MaintenanceMetadataContractTest {
  private static final Instant AT = Instant.parse("2026-11-01T00:00:00.123456Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 91), AT);
  private static final MaintenanceActivation ACTIVATION = new MaintenanceActivation(RUN, new UUID(0, 92));

  @Test
  void maintenanceMetadata001StorageNamesRetainExactAsciiSyntaxAndRedactBothFields() {
    for (String name : List.of("a", "_", "pgpt_owner-01", "a".repeat(32))) {
      String group = "pgpt_group";
      var value = new StorageIdentity(name, group);
      assertSame(name, value.owner());
      assertSame(group, value.group());
      assertEquals("StorageIdentity[REDACTED]", value.toString());
    }
  }

  @Test
  void maintenanceMetadata002StorageNamesRejectNullLengthAndEveryInvalidCharacterClass() {
    assertThrows(NullPointerException.class, () -> new StorageIdentity(null, "pgpt_group"));
    assertThrows(NullPointerException.class, () -> new StorageIdentity("pgpt_owner", null));
    for (String name : List.of("", "A", "1a", "-a", "a".repeat(33), "a b", "a/b", "a\n", "あ")) {
      assertEquals("invalid storage OS identity",
          assertThrows(IllegalArgumentException.class,
              () -> new StorageIdentity(name, "pgpt_group")).getMessage());
      assertEquals("invalid storage OS identity",
          assertThrows(IllegalArgumentException.class,
              () -> new StorageIdentity("pgpt_owner", name)).getMessage());
    }
  }

  @Test
  void maintenanceMetadata003SummaryRetainsCountsAndCompleteFlagWithoutCertifyingAnyGate() {
    for (CleanupCounts counts : List.of(new CleanupCounts(0, 0, 0),
        new CleanupCounts(5, 2, 3), new CleanupCounts(Long.MAX_VALUE, 0, Long.MAX_VALUE))) {
      for (boolean complete : new boolean[] {false, true}) {
        var value = new InspectionSummary(RUN, counts, complete);
        assertSame(RUN, value.run());
        assertSame(counts, value.counts());
        assertEquals(complete, value.complete());
        assertEquals("InspectionSummary[observation=<redacted>]", value.toString());
      }
    }
  }

  @Test
  void maintenanceMetadata004SummaryRequiresBothRunAndCountsEvenWhenNotComplete() {
    var counts = new CleanupCounts(0, 0, 0);
    for (boolean complete : new boolean[] {false, true}) {
      assertThrows(NullPointerException.class, () -> new InspectionSummary(null, counts, complete));
      assertThrows(NullPointerException.class, () -> new InspectionSummary(RUN, null, complete));
    }
  }

  @Test
  void maintenanceMetadata005StateRetainsEmptyOrEqualActivationCompletionWithoutAuthority() {
    var empty = Optional.<MaintenanceCompletion>empty();
    var pending = new MaintenanceRunState(ACTIVATION, empty);
    assertSame(ACTIVATION, pending.activation());
    assertSame(empty, pending.completion());
    assertEquals("MaintenanceRunState[redacted]", pending.toString());
    for (MaintenanceCompletion.Outcome outcome :
        List.of(MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.WARNING)) {
      var equalButDistinct =
          new MaintenanceActivation(new BatchRun(new UUID(0, 91), AT), new UUID(0, 92));
      var selected = Optional.of(new MaintenanceCompletion(equalButDistinct, AT.plusSeconds(1), outcome));
      var value = new MaintenanceRunState(ACTIVATION, selected);
      assertSame(ACTIVATION, value.activation());
      assertSame(selected, value.completion());
      assertEquals(outcome, value.completion().orElseThrow().outcome());
      assertEquals("MaintenanceRunState[redacted]", value.toString());
    }
  }

  @Test
  void maintenanceMetadata006StateRejectsNullAndBothRunOrActivationMismatches() {
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(ACTIVATION, null));
    var otherRun = new BatchRun(new UUID(0, 93), AT);
    for (MaintenanceActivation other : List.of(
        new MaintenanceActivation(RUN, new UUID(0, 93)),
        new MaintenanceActivation(otherRun, new UUID(0, 92)))) {
      var completion = new MaintenanceCompletion(other, AT.plusSeconds(1), MaintenanceCompletion.Outcome.SUCCESS);
      assertEquals("maintenance completion identity differs",
          assertThrows(IllegalArgumentException.class,
              () -> new MaintenanceRunState(ACTIVATION, Optional.of(completion))).getMessage());
    }
  }
}
