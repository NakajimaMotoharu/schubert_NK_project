package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation.Evidence;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-P01810-CATALOG-062A..C: detached value ownership and fixed general diagnostics. */
final class ArtemisStartupEvidenceValueTest {
  private static final String ADDRESS = "synthetic-queue";
  private static final String ROLE = "synthetic-role";
  private static final String PERMISSION = "consume";
  private static final String FIELD = "synthetic-field";
  private static final String BEFORE = "synthetic-initial-value";
  private static final String AFTER = "synthetic-replacement";
  private static final String DIAGNOSTIC = "ArtemisEvidence[observations=<redacted>]";
  private static final ArtemisQueuePressureClient.Value PRESSURE =
      new ArtemisQueuePressureClient.Value(3, 15, ArtemisQueuePressureClient.Pressure.WARNING);
  private static final Map<String, String> EXPECTED_FIELDS = Map.of(FIELD, BEFORE);

  @Test
  void ownsAllNestedValueInputsBeforeAndAfterCallerMutatesThem() {
    var topologyFields = new HashMap<>(EXPECTED_FIELDS);
    var settingsFields = new HashMap<>(EXPECTED_FIELDS);
    var broker = new HashMap<>(EXPECTED_FIELDS);
    var acceptor = new HashMap<>(EXPECTED_FIELDS);
    var permissions = new HashMap<>(Map.of(PERMISSION, true));
    var roles = new HashMap<>(Map.of(ROLE, permissions));
    var pressure = new HashMap<>(Map.of(ADDRESS, PRESSURE));
    var evidence =
        new Evidence(
            Map.of(ADDRESS, topologyFields),
            broker,
            Map.of(ADDRESS, settingsFields),
            acceptor,
            Map.of(ADDRESS, roles),
            pressure);

    topologyFields.put(FIELD, AFTER);
    settingsFields.clear();
    broker.clear();
    acceptor.clear();
    permissions.put(PERMISSION, false);
    roles.clear();
    pressure.clear();

    assertEquals(Map.of(ADDRESS, EXPECTED_FIELDS), evidence.topology());
    assertEquals(Map.of(ADDRESS, EXPECTED_FIELDS), evidence.settings());
    assertEquals(EXPECTED_FIELDS, evidence.broker());
    assertEquals(EXPECTED_FIELDS, evidence.acceptor());
    assertEquals(Map.of(ADDRESS, Map.of(ROLE, Map.of(PERMISSION, true))), evidence.roles());
    assertEquals(Map.of(ADDRESS, PRESSURE), evidence.pressure());
    assertThrows(
        UnsupportedOperationException.class, () -> evidence.topology().get(ADDRESS).clear());
    assertThrows(UnsupportedOperationException.class, () -> evidence.roles().get(ADDRESS).clear());
    assertEquals(DIAGNOSTIC, evidence.toString());
  }

  @Test
  void comparesOwnedValueDataWhileItsGeneralDiagnosticsStayFixed() {
    Evidence original = evidence(BEFORE);
    Evidence equivalent = evidence(BEFORE);
    Evidence different = evidence(AFTER);

    assertEquals(original, equivalent);
    var lookup = new HashMap<Evidence, String>();
    lookup.put(original, "retained");
    assertEquals("retained", lookup.get(equivalent));
    assertNotEquals(original, different);
    assertEquals(DIAGNOSTIC, original.toString());
    assertEquals(DIAGNOSTIC, different.toString());
  }

  @Test
  void rejectsMissingNestedInputsWhileTakingOwnership() {
    Map<String, String> missingField = new HashMap<>();
    missingField.put(FIELD, null);
    Map<String, Boolean> missingPermission = new HashMap<>();
    missingPermission.put(PERMISSION, null);
    Map<String, ArtemisQueuePressureClient.Value> missingPressure = new HashMap<>();
    missingPressure.put(ADDRESS, null);

    assertThrows(
        NullPointerException.class,
        () ->
            new Evidence(
                Map.of(ADDRESS, missingField), Map.of(), Map.of(), Map.of(), Map.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            new Evidence(
                Map.of(),
                Map.of(),
                Map.of(),
                Map.of(),
                Map.of(ADDRESS, Map.of(ROLE, missingPermission)),
                Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new Evidence(Map.of(), Map.of(), Map.of(), Map.of(), Map.of(), missingPressure));
  }

  private static Evidence evidence(String value) {
    return new Evidence(
        Map.of(ADDRESS, Map.of(FIELD, value)),
        EXPECTED_FIELDS,
        Map.of(),
        Map.of(),
        Map.of(),
        Map.of());
  }
}
