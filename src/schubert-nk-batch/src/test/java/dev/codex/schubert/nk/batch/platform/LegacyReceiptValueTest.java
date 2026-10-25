package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-RETDATA-001 / SS341343: legacy metadata never supplies genuine typed evidence. */
final class LegacyReceiptValueTest {
  @Test
  void retdata001LegacyZeroDoesNotManufactureTypedOrStoppedReceipt() throws Exception {
    Object baseline = new Object();
    for (boolean zero : new boolean[] {false, true}) {
      var queries = new AtomicInteger();
      var receipt =
          new MorningBackupUnitCycle.Receipt() {
            @Override
            public Object capture() {
              throw new AssertionError("data-only test must not capture an actual receipt");
            }

            @Override
            public boolean freshZero(Object actual) {
              assertSame(baseline, actual);
              queries.incrementAndGet();
              return zero;
            }
          };
      assertEquals(Optional.empty(), receipt.observed(baseline));
      var missing = assertThrows(IOException.class, () -> receipt.requirePresent(null));
      assertEquals("typed receipt unavailable", missing.getMessage());
      assertNull(missing.getCause());
      assertEquals(0, missing.getSuppressed().length);
      var stopped = assertThrows(IOException.class, () -> receipt.stopped(baseline, null));
      assertEquals("stopped Backup receipt unavailable", stopped.getMessage());
      assertNull(stopped.getCause());
      assertEquals(0, stopped.getSuppressed().length);
      assertEquals(0, queries.get());
      assertEquals(
          zero ? Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS) : Optional.empty(),
          receipt.terminal(baseline));
      assertEquals(1, queries.get());
      assertEquals(Optional.empty(), receipt.observed(baseline));
      assertEquals(1, queries.get());
    }
  }
}
