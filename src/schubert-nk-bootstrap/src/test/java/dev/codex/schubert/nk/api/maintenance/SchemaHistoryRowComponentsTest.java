package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission.Row;
import org.junit.jupiter.api.Test;

/** PT-OPS-SCHEMA015: direct component and equality checks for fixed, synthetic history rows. */
final class SchemaHistoryRowComponentsTest {
  private static final String SCHEMA = "SCHEMA";
  private static final String SCHEMA_SCRIPT = "\"schubert_meta\"";
  private static final String SQL = "SQL";
  private static final String VERSION = "029";
  private static final String SCRIPT = "V029__fixture.sql";
  private static final int CHECKSUM = -2919;

  @Test
  void opsSchema015BothRowKindsRetainValuesAndCompareByContent() {
    var schema = new Row(0, null, SCHEMA, SCHEMA_SCRIPT, null, true);
    assertEquals(0, schema.installedRank());
    assertNull(schema.version());
    assertEquals(SCHEMA, schema.type());
    assertEquals(SCHEMA_SCRIPT, schema.script());
    assertNull(schema.checksum());
    assertEquals(new Row(0, null, SCHEMA, SCHEMA_SCRIPT, null, true), schema);

    var versioned = new Row(2, VERSION, SQL, SCRIPT, CHECKSUM, true);
    assertEquals(2, versioned.installedRank());
    assertEquals(VERSION, versioned.version());
    assertEquals(SQL, versioned.type());
    assertEquals(SCRIPT, versioned.script());
    assertEquals(Integer.valueOf(CHECKSUM), versioned.checksum());
    var equal = new Row(2, VERSION, SQL, SCRIPT, CHECKSUM, true);
    assertEquals(equal, versioned);
    assertEquals(versioned, equal);

    assertNotEquals(versioned, schema);
    assertNotEquals(versioned, versioned.script());
    assertNotEquals(versioned, new Row(3, VERSION, SQL, SCRIPT, CHECKSUM, true));
    assertNotEquals(versioned, new Row(2, VERSION, SQL, SCRIPT, 0, true));
    assertNotEquals(versioned, new Row(2, VERSION, SQL, "V029__other.sql", CHECKSUM, true));
    assertNotEquals(versioned, new Row(2, "030", SQL, "V030__fixture.sql", CHECKSUM, true));
  }
}
