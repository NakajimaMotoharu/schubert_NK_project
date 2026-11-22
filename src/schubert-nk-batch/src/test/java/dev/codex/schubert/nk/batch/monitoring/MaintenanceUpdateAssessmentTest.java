package dev.codex.schubert.nk.batch.monitoring;

import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.CONDITIONS_MET;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.CONDITIONS_MET_WITH_WARNING;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.KEEP_PRIVATE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.CONFIRMED_SAFE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.UNSAFE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.UNVERIFIED;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult.SUCCESS;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult.WARNING;
import static org.junit.jupiter.api.Assertions.assertEquals;

import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.SafetyChecks;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult;
import java.util.List;
import org.junit.jupiter.api.Test;

final class MaintenanceUpdateAssessmentTest {
  private static final SafetyChecks ALL_CONFIRMED =
      new SafetyChecks(
          CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE);

  @Test
  void u01SuccessfulUpdateMeetsAllFiveVerifiedConditions() {
    assertEquals(CONDITIONS_MET, MaintenanceUpdateAssessment.assess(SUCCESS, ALL_CONFIRMED));
  }

  @Test
  void u02UpdateWarningRemainsVisibleWithAllFiveConditionsVerified() {
    assertEquals(
        CONDITIONS_MET_WITH_WARNING, MaintenanceUpdateAssessment.assess(WARNING, ALL_CONFIRMED));
  }

  @Test
  void u03EachUnsafeConditionKeepsBothUpdateOutcomesPrivate() {
    List<SafetyChecks> unsafeChecks =
        List.of(
            new SafetyChecks(
                UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE));
    for (SafetyChecks checks : unsafeChecks) {
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, checks));
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(WARNING, checks));
    }
  }

  @Test
  void u04MissingUpdateOrCheckReceiptCannotMeetTheConditions() {
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(null, ALL_CONFIRMED));
    assertEquals(
        KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(UpdateResult.UNVERIFIED, ALL_CONFIRMED));
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, null));
  }

  @Test
  void u05EachUnverifiedObservationKeepsTheWarningPrivate() {
    List<SafetyChecks> unverifiedChecks =
        List.of(
            new SafetyChecks(
                UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED));
    for (SafetyChecks checks : unverifiedChecks) {
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(WARNING, checks));
    }
  }

  @Test
  void u06NullObservationsRemainUnverifiedAndCannotRetainAnOldSuccess() {
    SafetyChecks absent = new SafetyChecks(null, null, null, null, null);
    assertEquals(UNVERIFIED, absent.packageManagerLock());
    assertEquals(UNVERIFIED, absent.packageConsistency());
    assertEquals(UNVERIFIED, absent.filesystem());
    assertEquals(UNVERIFIED, absent.bootPartition());
    assertEquals(UNVERIFIED, absent.kernelAndInitramfs());
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, absent));
  }
}
