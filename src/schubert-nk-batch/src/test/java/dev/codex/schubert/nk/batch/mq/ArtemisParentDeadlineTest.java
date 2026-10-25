package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import org.junit.jupiter.api.Test;

/** SS321/341/343 SSC125 BUG370/YKT291 EXPARENT005; literal nanosecond/timeout oracle. */
final class ArtemisParentDeadlineTest {
  @Test
  void eachExchangeBorrowsActualRemainingAndNeverRoundsUp() throws Exception {
    long[] remaining = {5_000_000_000L};
    MaintenanceOwnerFrame.Guard parent = () -> remaining[0];
    assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
    assertEquals(
        "done",
        ArtemisManagementReadinessClient.withParentDeadline(
            parent,
            () -> {
              assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
              remaining[0] = 1_999_999_999L;
              assertEquals(1999, ArtemisManagementReadinessClient.requestTimeoutMillis());
              remaining[0] = 1_000_000L;
              assertEquals(1, ArtemisManagementReadinessClient.requestTimeoutMillis());
              remaining[0] = 999_999L;
              assertThrows(
                  IOException.class, ArtemisManagementReadinessClient::requestTimeoutMillis);
              remaining[0] = 1;
              assertThrows(
                  IOException.class, ArtemisManagementReadinessClient::requestTimeoutMillis);
              remaining[0] = 0;
              assertThrows(
                  IOException.class, ArtemisManagementReadinessClient::requestTimeoutMillis);
              remaining[0] = 1_000_000_000L;
              return "done";
            }));
    assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
  }

  @Test
  void exceptionExpiryNestedAndOtherThreadNeverEscapeOwnerLifetime() throws Exception {
    long[] remaining = {1_000_000_000L};
    MaintenanceOwnerFrame.Guard parent = () -> remaining[0];
    assertThrows(
        IOException.class,
        () ->
            ArtemisManagementReadinessClient.withParentDeadline(
                parent,
                () -> {
                  throw new IOException("independent failure");
                }));
    assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
    ArtemisManagementReadinessClient.withParentDeadline(
        parent,
        () -> {
          assertThrows(
              IOException.class,
              () ->
                  ArtemisManagementReadinessClient.withParentDeadline(
                      () -> 5_000_000_000L, () -> fail("no nested replacement budget")));
          assertEquals(1000, ArtemisManagementReadinessClient.requestTimeoutMillis());
          long[] other = {-1};
          Thread thread =
              new Thread(
                  () -> {
                    try {
                      other[0] = ArtemisManagementReadinessClient.requestTimeoutMillis();
                    } catch (IOException known) {
                      throw new AssertionError(known);
                    }
                  });
          thread.start();
          try {
            thread.join();
          } catch (InterruptedException known) {
            throw new AssertionError(known);
          }
          assertEquals(2000, other[0]);
          return true;
        });
    assertThrows(
        IOException.class,
        () ->
            ArtemisManagementReadinessClient.withParentDeadline(
                parent,
                () -> {
                  remaining[0] = 0;
                  return true;
                }));
    assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
    assertThrows(
        IOException.class,
        () ->
            ArtemisManagementReadinessClient.withParentDeadline(
                parent, () -> fail("no operation after exhausted parent")));
    assertThrows(
        NullPointerException.class,
        () -> ArtemisManagementReadinessClient.withParentDeadline(null, () -> true));
    assertThrows(
        NullPointerException.class,
        () -> ArtemisManagementReadinessClient.withParentDeadline(() -> 1, null));
    assertThrows(
        NullPointerException.class,
        () -> ArtemisManagementReadinessClient.withParentDeadline(() -> 1, () -> null));
    assertEquals(2000, ArtemisManagementReadinessClient.requestTimeoutMillis());
  }
}
