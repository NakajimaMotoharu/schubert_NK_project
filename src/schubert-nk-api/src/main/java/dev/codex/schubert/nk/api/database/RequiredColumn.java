package dev.codex.schubert.nk.api.database;

import java.sql.SQLDataException;
import org.jspecify.annotations.Nullable;

/**
 * Required JDBC result contract, independent of a driver's null annotations. Trace:
 * NK-DAT-001/NK-MSG-002, RD DAT-009, UI241/242, SS331/332/354, PT-QUALITY-002, BUG-016/YKT-013. SQL
 * NULL is an integrity failure, never a default value.
 */
public final class RequiredColumn {
  private RequiredColumn() {
    throw new AssertionError("static namespace");
  }

  /** Returns the required value or a redacted SQLSTATE 22004 integrity failure. */
  public static <T> T requireValue(@Nullable T value) throws SQLDataException {
    if (value == null) {
      throw new SQLDataException("required database value is missing", "22004");
    }
    return value;
  }
}
