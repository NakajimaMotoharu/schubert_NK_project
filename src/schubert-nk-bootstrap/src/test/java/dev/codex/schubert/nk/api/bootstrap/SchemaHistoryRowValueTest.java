package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission.Row;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class SchemaHistoryRowValueTest {
  @Test
  @DisplayName("PT-OPS-SCHEMAROW001 schema and SQL preserve distinct typed fields")
  void preservesSchemaAndSqlFields() {
    var schema = new Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true);
    assertEquals(0, schema.installedRank());
    assertEquals("SCHEMA", schema.type());
    assertNull(schema.version());
    assertNull(schema.checksum());

    var sql = new Row(5, "029", "SQL", "V029__synthetic.sql", -42, true);
    assertEquals(5, sql.installedRank());
    assertEquals("SQL", sql.type());
    assertEquals("029", sql.version());
    assertEquals(-42, sql.checksum());
  }

  @Test
  @DisplayName("PT-OPS-SCHEMAROW002 an unequal checksum distinguishes literal rows")
  void comparesAllRowValuesIncludingChecksum() {
    var first = new Row(5, "029", "SQL", "V029__synthetic.sql", -42, true);
    var same = new Row(5, "029", "SQL", "V029__synthetic.sql", -42, true);
    var different = new Row(5, "029", "SQL", "V029__synthetic.sql", -41, true);
    assertEquals(first, same);
    assertEquals(first.hashCode(), same.hashCode());
    assertNotEquals(first, different);
  }
}
