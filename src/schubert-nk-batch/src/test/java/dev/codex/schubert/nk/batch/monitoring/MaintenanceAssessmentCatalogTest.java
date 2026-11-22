package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-OPS-MAINT-CATALOG001/002; UI251 §3, SS341 §4.1/4.2; closed observation values. */
final class MaintenanceAssessmentCatalogTest {
  @Test
  void catalog001RebootAndStopValuesHaveStableNamesAndOrder() {
    checkCatalog(
        List.of("WAITING", "COMPLETE", "CRITICAL", "INVALID_OBSERVATION"),
        MaintenanceRebootWatch.Decision::values,
        MaintenanceRebootWatch.Decision::valueOf);
    checkCatalog(
        List.of("CADDY", "WEB", "API", "ARTEMIS", "POSTGRESQL"),
        MaintenanceStopAssessment.Stage::values,
        MaintenanceStopAssessment.Stage::valueOf);
    checkCatalog(
        List.of("CONFIRMED", "FAILED", "TIMED_OUT", "UNVERIFIED"),
        MaintenanceStopAssessment.Result::values,
        MaintenanceStopAssessment.Result::valueOf);
  }

  @Test
  void catalog002UpdateValuesRejectUnknownOrMissingNames() {
    checkCatalog(
        List.of("SUCCESS", "WARNING", "UNVERIFIED"),
        MaintenanceUpdateAssessment.UpdateResult::values,
        MaintenanceUpdateAssessment.UpdateResult::valueOf);
    checkCatalog(
        List.of("CONFIRMED_SAFE", "UNSAFE", "UNVERIFIED"),
        MaintenanceUpdateAssessment.Observation::values,
        MaintenanceUpdateAssessment.Observation::valueOf);
    checkCatalog(
        List.of("CONDITIONS_MET", "CONDITIONS_MET_WITH_WARNING", "KEEP_PRIVATE"),
        MaintenanceUpdateAssessment.Decision::values,
        MaintenanceUpdateAssessment.Decision::valueOf);
  }

  private static <E extends Enum<E>> void checkCatalog(
      List<String> expected, Supplier<E[]> values, Function<String, E> valueOf) {
    E[] catalog = values.get();
    assertEquals(expected, Arrays.stream(catalog).map(Enum::name).toList());
    for (int index = 0; index < expected.size(); index++) {
      assertEquals(catalog[index], valueOf.apply(expected.get(index)));
    }
    assertThrows(IllegalArgumentException.class, () -> valueOf.apply("UNKNOWN_STATE"));
    assertThrows(IllegalArgumentException.class, () -> valueOf.apply(""));
    assertThrows(NullPointerException.class, () -> valueOf.apply(null));
    catalog[0] = null;
    assertEquals(expected, Arrays.stream(values.get()).map(Enum::name).toList());
  }
}
