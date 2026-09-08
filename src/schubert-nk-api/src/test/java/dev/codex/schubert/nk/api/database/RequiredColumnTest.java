package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.sql.SQLDataException;
import java.time.Instant;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Independent null/error oracle for the JDBC boundary; no production-derived expected values. */
final class RequiredColumnTest {
  @Test
  @DisplayName("PT-QUALITY-002 required JDBC values retain identity and SQL NULL fails redacted")
  void requiredValuesRetainIdentityAndNullFailsWithSqlState() throws Exception {
    String text = "synthetic";
    Instant time = Instant.parse("2026-09-07T00:00:00Z");
    byte[] bytes = {1, 2, 3};
    assertSame(text, RequiredColumn.requireValue(text));
    assertSame(time, RequiredColumn.requireValue(time));
    assertSame(bytes, RequiredColumn.requireValue(bytes));
    SQLDataException failure =
        assertThrows(SQLDataException.class, () -> RequiredColumn.requireValue(null));
    assertEquals("22004", failure.getSQLState());
    assertEquals("required database value is missing", failure.getMessage());
    assertNull(failure.getCause());
  }
}
