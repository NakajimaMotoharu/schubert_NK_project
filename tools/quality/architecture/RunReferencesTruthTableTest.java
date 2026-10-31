package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-OPS-REF-FLAGS-001..003; SS331 section3.12; independent data, no repository/DB/lookup. */
public final class RunReferencesTruthTableTest {
  private record Vector(boolean history, boolean inbox, boolean log, boolean consistent,
                        boolean allowed, boolean any) {}

  private static final List<Vector> VECTORS = List.of(
      new Vector(false, false, false, false, false, false),
      new Vector(false, false, false, true,  true,  false),
      new Vector(false, false, true,  false, true,  true),
      new Vector(false, false, true,  true,  true,  true),
      new Vector(false, true,  false, false, true,  true),
      new Vector(false, true,  false, true,  true,  true),
      new Vector(false, true,  true,  false, true,  true),
      new Vector(false, true,  true,  true,  true,  true),
      new Vector(true,  false, false, false, true,  true),
      new Vector(true,  false, false, true,  true,  true),
      new Vector(true,  false, true,  false, true,  true),
      new Vector(true,  false, true,  true,  true,  true),
      new Vector(true,  true,  false, false, true,  true),
      new Vector(true,  true,  false, true,  true,  true),
      new Vector(true,  true,  true,  false, true,  true),
      new Vector(true,  true,  true,  true,  true,  true));

  @Test
  void flags001ConstructorAndFourFieldsMatchEveryLiteralTuple() {
    assertEquals(16, VECTORS.size());
    for (var row : VECTORS) {
      if (!row.allowed()) {
        var error = assertThrows(IllegalArgumentException.class,
            () -> new RunReferences(row.history(), row.inbox(), row.log(), row.consistent()));
        assertEquals("inconsistent run reference projection", error.getMessage());
        continue;
      }
      var actual = new RunReferences(row.history(), row.inbox(), row.log(), row.consistent());
      assertEquals(row.history(), actual.hasBatchHistory());
      assertEquals(row.inbox(), actual.hasInboxProgress());
      assertEquals(row.log(), actual.hasLogProgress());
      assertEquals(row.consistent(), actual.identityConsistent());
    }
  }

  @Test
  void flags002AnyReferenceUsesOnlyTheThreeIndependentPresenceFlags() {
    for (var row : VECTORS) {
      if (!row.allowed()) continue;
      var actual = new RunReferences(row.history(), row.inbox(), row.log(), row.consistent());
      assertEquals(row.any(), actual.anyReference());
    }
  }

  @Test
  void flags003DiagnosticIsFixedForAllFifteenAdmittedTuples() {
    for (var row : VECTORS) {
      if (!row.allowed()) continue;
      var actual = new RunReferences(row.history(), row.inbox(), row.log(), row.consistent());
      assertEquals("RunReferences[observation=<redacted>]", actual.toString());
      assertFalse(actual.toString().contains("true"));
      assertFalse(actual.toString().contains("false"));
    }
  }
}
