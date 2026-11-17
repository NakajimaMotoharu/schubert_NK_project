package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.io.IOException;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;

/** PT-SUM-GRAPH001 / SS332 typed SQL pair: public nonfatal mixed graph, no DB/Root action. */
class InspectionSummaryGraphContractTest {
  @Test
  void nonfatalMixedCauseSuppressedCycleRemainsKnownAndUnmodified() {
    var primary = new SQLException("PUBLIC-SQL");
    var bridge = new IOException("PUBLIC-IO");
    var ordinary = new IllegalStateException("PUBLIC-STATE");
    primary.initCause(bridge);
    bridge.initCause(primary);
    primary.addSuppressed(ordinary);
    ordinary.initCause(bridge);
    var cleanup = new SQLException("PUBLIC-CLEANUP");
    var tail = new Exception("PUBLIC-NONSQL-TAIL");
    cleanup.initCause(tail);

    assertFalse(JdbcResourceFailures.replace(primary, cleanup));
    assertSame(bridge, primary.getCause());
    assertSame(primary, bridge.getCause());
    assertSame(bridge, ordinary.getCause());
    assertSame(tail, cleanup.getCause());
    assertArrayEquals(new Throwable[] {ordinary}, primary.getSuppressed());
    assertArrayEquals(new Throwable[0], cleanup.getSuppressed());
  }
}
