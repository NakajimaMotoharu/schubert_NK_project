package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS343/SSC111117; PT-CORR-EREQ-001..002. Immutable public claims, no I/O or permission. */
final class ExpiryRequestBoundaryTest {
  @Test
  void expiryBoundary001EachPreviouslyUnverifiedConstructorIdentityRejects() {
    UUID run = UUID.fromString("38100000-2222-4333-8444-555555555555");
    UUID activation = UUID.fromString("38100000-6666-4777-8888-999999999999");
    UUID boot = UUID.fromString("38100000-3333-4333-8444-555555555555");
    UUID epoch = UUID.fromString("38100000-4444-4333-8444-555555555555");
    UUID nil = new UUID(0, 0);
    Instant cutoff = Instant.parse("2026-09-30T00:00:00Z");
    Instant start = Instant.parse("2026-09-30T00:00:01Z");
    var ordinary =
        new CleanupWorkerRequest.Expiry(
            run, activation, cutoff, boot, epoch, "1".repeat(32), 42, 1, start, false);
    assertArrayEquals(
        ExpiryWorkerRequestTest.GOLDEN.getBytes(StandardCharsets.US_ASCII), ordinary.encode());
    assertEquals(run, ordinary.run());
    assertEquals(activation, ordinary.activation());
    assertEquals(cutoff, ordinary.cutoff());
    assertEquals(boot, ordinary.boot());
    assertEquals(epoch, ordinary.epoch());
    assertEquals("1".repeat(32), ordinary.brokerInvocation());
    assertEquals(42, ordinary.stepId());
    assertEquals(1, ordinary.attempt());
    assertEquals(start, ordinary.started());
    assertFalse(ordinary.skipped());
    assertTrue(ordinary.prior().isEmpty());
    for (int changed = 0; changed < 4; changed++) {
      UUID suppliedRun = changed == 0 ? nil : run;
      UUID suppliedActivation = changed == 1 ? nil : activation;
      UUID suppliedBoot = changed == 2 ? nil : boot;
      String suppliedBroker = changed == 3 ? "X".repeat(32) : "1".repeat(32);
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new CleanupWorkerRequest.Expiry(
                      suppliedRun,
                      suppliedActivation,
                      cutoff,
                      suppliedBoot,
                      epoch,
                      suppliedBroker,
                      42,
                      1,
                      start,
                      false));
      assertEquals("cleanup request invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  @Test
  void expiryBoundary002DelAndSameLengthProfileTailRejectAndEraseOwnedBytes() {
    for (String literal :
        List.of(
            "\u007f",
            ExpiryWorkerRequestTest.GOLDEN + "X",
            ExpiryWorkerRequestTest.SKIP_GOLDEN + "X")) {
      byte[] owned = literal.getBytes(StandardCharsets.US_ASCII);
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(owned));
      assertEquals("cleanup request invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertArrayEquals(new byte[owned.length], owned);
    }
  }
}
