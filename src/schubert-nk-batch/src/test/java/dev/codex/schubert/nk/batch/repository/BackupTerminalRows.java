package dev.codex.schubert.nk.batch.repository;

import java.lang.reflect.Proxy;
import java.sql.ResultSet;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** SS332/341: fixed synthetic Terminal row shared by BKPPORT010 and ISSCOMP001..003. */
final class BackupTerminalRows {
  private BackupTerminalRows() {}

  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  static final Instant END = Instant.parse("2026-09-13T02:00:01Z");
  static final BatchStepAttempt DB =
      new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 2, START, false);

  static Map<String, Object> literal() {
    var m = new HashMap<String, Object>();
    m.put("id", 1L);
    m.put("run_id", RUN.id());
    m.put("business_date", LocalDate.of(2026, 9, 13));
    m.put("step", "BACKUP_DB");
    m.put("attempt", 2);
    m.put("started_at", START.atOffset(ZoneOffset.UTC));
    m.put("ended_at", END.atOffset(ZoneOffset.UTC));
    m.put("status", "SUCCESS");
    m.put("target_count", 1L);
    m.put("success_count", 1L);
    m.put("failure_count", 0L);
    m.put("byte_count", 26L);
    m.put("error_code", null);
    m.put("error_summary", null);
    return m;
  }

  static ResultSet row(Map<String, Object> input) {
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, args) -> {
              if (m.getName().equals("getObject") || m.getName().equals("getString"))
                return input.get(args[0]);
              throw new AssertionError("unexpected JDBC operation " + m.getName());
            });
  }
}
