package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxJmsSender;
import dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcher;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.time.Clock;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** SS316/PT-NHOLD316005: self-owned unstarted Outbox, no DB/JMS/Root invocation. */
final class ApiPreparationOwnerTest {
  private static OwnedOutboxDispatcher create() {
    return OwnedOutboxDispatcher.create(
        new OutboxDispatcher(
            () -> {
              throw new AssertionError("no database before outbox start");
            },
            () -> {
              throw new AssertionError("no JMS before outbox start");
            },
            new JdbcOutboxRepository(),
            new OutboxJmsSender(),
            Clock.systemUTC()),
        "fixture-owner");
  }

  @Test
  void prep316010NullPortsAndFactoryFailureNeverInvokeBody() {
    for (boolean retaining : List.of(false, true)) {
      var acquisitions = new AtomicInteger();
      Supplier<OwnedOutboxDispatcher> forbidden =
          () -> {
            acquisitions.incrementAndGet();
            throw new AssertionError("invalid operation cannot acquire");
          };
      assertThrows(
          NullPointerException.class,
          () -> ApiApplicationPreparation.withOutbox(null, ignored -> Boolean.TRUE, retaining));
      assertThrows(
          NullPointerException.class,
          () -> ApiApplicationPreparation.withOutbox(forbidden, null, retaining));
      assertEquals(0, acquisitions.get());
      var marker = new IllegalStateException("fixture acquisition");
      var body = new AtomicInteger();
      assertSame(
          marker,
          assertThrows(
              IllegalStateException.class,
              () ->
                  ApiApplicationPreparation.withOutbox(
                      () -> {
                        throw marker;
                      },
                      owner -> {
                        body.incrementAndGet();
                        return Boolean.TRUE;
                      },
                      retaining)));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.withOutbox(
                  () -> null,
                  owner -> {
                    body.incrementAndGet();
                    return Boolean.TRUE;
                  },
                  retaining));
      assertEquals(0, body.get());
    }
    assertThrows(
        NullPointerException.class,
        () ->
            ApiApplicationPreparation.executeRetainingUnknown(
                null, null, null, null, 0, null, null, null));
  }

  @Test
  void prep316011KnownCloseStopsTheSameOwnedDispatcherBeforeReturning() throws Exception {
    for (boolean retaining : List.of(false, true)) {
      var captured = new AtomicReference<OwnedOutboxDispatcher>();
      var bodies = new AtomicInteger();
      ApiApplicationPreparation.withOutbox(
          () -> {
            var owner = create();
            captured.set(owner);
            return owner;
          },
          owner -> {
            assertSame(captured.get(), owner);
            assertFalse(owner.healthy());
            bodies.incrementAndGet();
            return Boolean.TRUE;
          },
          retaining);
      assertEquals(1, bodies.get());
      assertFalse(captured.get().healthy());
      assertThrows(IllegalStateException.class, captured.get()::start);
      captured.get().close();
    }
  }

  @Test
  void prep316012BodyFailureClosesOwnerAndPreservesOrdinaryTwrPrecedence() {
    for (boolean retaining : List.of(false, true)) {
      for (Throwable marker :
          List.of(
              new IOException("fixture private IO"),
              new IllegalStateException("fixture runtime"),
              new AssertionError("fixture error"))) {
        var owner = create();
        try {
          var failure =
              assertThrows(
                  Throwable.class,
                  () ->
                      ApiApplicationPreparation.withOutbox(
                          () -> owner,
                          ignored -> {
                            if (marker instanceof IOException io) throw io;
                            if (marker instanceof RuntimeException runtime) throw runtime;
                            throw (Error) marker;
                          },
                          retaining));
          if (retaining && marker instanceof IOException) {
            assertEquals(StorageIoException.class, failure.getClass());
            assertEquals(
                StorageIoException.Reason.UNAVAILABLE, ((StorageIoException) failure).reason());
            assertNull(failure.getCause());
            assertFalse(failure.getMessage().contains("fixture private"));
          } else assertSame(marker, failure);
          assertThrows(IllegalStateException.class, owner::start);
        } finally {
          owner.close();
        }
      }
    }
  }
}
