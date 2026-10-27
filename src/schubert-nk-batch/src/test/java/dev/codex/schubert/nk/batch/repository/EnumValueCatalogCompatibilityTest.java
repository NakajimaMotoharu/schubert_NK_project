package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.ObjectStreamClass;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG1478/YKT1237; SS331/332/341/343; PT-F03-ENUM-BAT001: no SQL or job execution. */
final class EnumValueCatalogCompatibilityTest {
  private static final String CLEAN_BATCH_RUN_NAME = "CLEAN_BATCH_RUN";

  @Test
  void bat001StepCleanupAndOutcomeCatalogsMatchIndependentTables() {
    assertEquals(
        List.of(
            "BACKUP_DB",
            "BACKUP_CONFIG",
            "CLEAN_NOTIFICATION",
            "CLEAN_QUESTION",
            "CLEAN_SESSION",
            "CLEAN_INBOX_OUTBOX",
            "CLEAN_LOG",
            CLEAN_BATCH_RUN_NAME,
            "CLEAN_TRANSFER",
            "CLEAN_EXPIRY"),
        Arrays.stream(BatchStep.values()).map(Enum::name).toList());
    assertEquals(
        List.of(true, true, false, false, false, false, false, false, false, false),
        Arrays.stream(BatchStep.values()).map(BatchStep::backup).toList());
    assertEquals(
        List.of(
            "NOTIFICATIONS",
            "QUESTIONS",
            "SESSIONS",
            "OUTBOX",
            "LOGS",
            "WEB_RECEIPTS",
            "BATCH_RUNS",
            "INBOX_PROGRESS",
            "LOG_PROGRESS"),
        Arrays.stream(CleanupKind.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            "schubert.maintenance_cleanup_notifications",
            "schubert.maintenance_cleanup_questions",
            "schubert.maintenance_cleanup_sessions",
            "schubert.maintenance_cleanup_message_stores",
            "schubert.maintenance_cleanup_logs",
            "schubert.maintenance_cleanup_web_receipt_references",
            "schubert.maintenance_cleanup_batch_runs",
            "schubert.maintenance_cleanup_inbox_progress",
            "schubert.maintenance_cleanup_log_progress"),
        Arrays.stream(CleanupKind.values()).map(CleanupKind::function).toList());
    assertEquals(
        List.of(1000, 1000, 1000, 1000, 10000, 1000, 1000, 1000, 1000),
        Arrays.stream(CleanupKind.values()).map(CleanupKind::maximumRows).toList());
    assertEquals(
        List.of(
            "CLEAN_NOTIFICATION",
            "CLEAN_QUESTION",
            "CLEAN_SESSION",
            "CLEAN_INBOX_OUTBOX",
            "CLEAN_LOG",
            CLEAN_BATCH_RUN_NAME,
            CLEAN_BATCH_RUN_NAME,
            CLEAN_BATCH_RUN_NAME,
            CLEAN_BATCH_RUN_NAME),
        Arrays.stream(CleanupKind.values()).map(value -> value.step().name()).toList());
    assertEquals(
        List.of("SUCCESS", "WARNING"),
        Arrays.stream(MaintenanceCompletion.Outcome.values()).map(Enum::name).toList());
    assertEquals(
        List.of(0, 10),
        Arrays.stream(MaintenanceCompletion.Outcome.values())
            .map(MaintenanceCompletion.Outcome::exitCode)
            .toList());
    for (Class<?> type :
        List.of(BatchStep.class, CleanupKind.class, MaintenanceCompletion.Outcome.class)) {
      var descriptor = ObjectStreamClass.lookup(type);
      assertEquals(0, descriptor.getFields().length, type.getName());
      assertEquals(0L, descriptor.getSerialVersionUID(), type.getName());
    }
  }
}
