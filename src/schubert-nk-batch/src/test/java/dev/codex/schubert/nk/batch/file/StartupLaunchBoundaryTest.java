package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS343/SSC137; PT-CORR-LAUNCH-001. Public data only, never an owner or startup authority. */
final class StartupLaunchBoundaryTest {
  @Test
  void launchBoundary001PositiveDelAndNonemptyFinalRowAreRejected() {
    for (String literal : List.of("\u007f", StartupLaunchRecordTest.GOLD + "X")) {
      byte[] input = literal.getBytes(StandardCharsets.US_ASCII);
      var failure = assertThrows(IOException.class, () -> StartupLaunchRecord.consume(input));
      assertEquals("startup launch unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
  }
}
