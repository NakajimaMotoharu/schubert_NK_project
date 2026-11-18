package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission.Row;
import org.junit.jupiter.api.Test;

/** PT-OPS-SCHEMA011: immutable projected row, fixed synthetic values only. */
final class SchemaHistoryRowValueTest {
  @Test
  void opsSchema011PublishedRowRetainsSuccessAndValueDiagnostics() {
    var row = new Row(1, "001", "SQL", "V001__fixture.sql", 19, true);
    assertTrue(row.success());
    assertEquals(
        "Row[installedRank=1, version=001, type=SQL, script=V001__fixture.sql, checksum=19, success=true]",
        row.toString());
    // Independent JDK25 record fold of literal public component hashes in declaration order.
    assertEquals(583197644, row.hashCode());
  }
}
