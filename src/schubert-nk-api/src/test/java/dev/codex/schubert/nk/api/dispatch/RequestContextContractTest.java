package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListRequestData;
import java.lang.reflect.Method;
import java.time.Instant;
import java.util.Arrays;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** PT-JMS-HCTX001..005 / SS311 §6.2 / SSC-477. */
final class RequestContextContractTest {
  private static final UUID MESSAGE_ID = new UUID(0, 17);
  private static final UUID HTTP_REQUEST_ID = new UUID(0, 43);
  private static final Instant RECEIVED_AT = Instant.parse("2026-11-22T14:00:05.012345Z");

  @Test
  @DisplayName("PT-JMS-HCTX001 verified actor and observed receipt values")
  void keepsActorAndTransportValuesWithoutDisplayingThem() {
    var actor = new AuthenticatedActor(23, "public-actor-fixture", Role.ADMIN);
    var context =
        new RequestContext(
            MESSAGE_ID,
            MESSAGE_ID,
            Optional.of(HTTP_REQUEST_ID),
            Optional.of(actor),
            RECEIVED_AT,
            7);
    assertEquals(MESSAGE_ID, context.messageId());
    assertEquals(MESSAGE_ID, context.correlationId());
    assertEquals(Optional.of(HTTP_REQUEST_ID), context.requestId());
    assertEquals(Optional.of(actor), context.actor());
    assertEquals(RECEIVED_AT, context.receivedAt());
    assertEquals(7, context.deliveryCount());
    assertEquals("RequestContext[<redacted>]", context.toString());
  }

  @Test
  @DisplayName("PT-JMS-HCTX002 absent HTTP identity and actor stay absent")
  void doesNotInferOptionalValuesFromAValidMessage() {
    var anonymous =
        new RequestContext(
            MESSAGE_ID, MESSAGE_ID, Optional.empty(), Optional.empty(), RECEIVED_AT, 1);
    assertEquals(Optional.empty(), anonymous.requestId());
    assertEquals(Optional.empty(), anonymous.actor());
    assertEquals(1, anonymous.deliveryCount());

    var authenticated =
        new RequestContext(
            MESSAGE_ID,
            MESSAGE_ID,
            Optional.empty(),
            Optional.of(new AuthenticatedActor(7, "public-user-fixture", Role.USER)),
            RECEIVED_AT,
            2);
    assertEquals(Optional.empty(), authenticated.requestId());
    assertEquals(Role.USER, authenticated.actor().orElseThrow().role());
  }

  @Test
  @DisplayName("PT-JMS-HCTX003 rejects absent containers and inconsistent root IDs")
  void rejectsInvalidInputBeforeConstructingAContext() {
    assertThrows(
        NullPointerException.class,
        () ->
            new RequestContext(
                null, MESSAGE_ID, Optional.empty(), Optional.empty(), RECEIVED_AT, 1));
    assertThrows(
        NullPointerException.class,
        () ->
            new RequestContext(
                MESSAGE_ID, null, Optional.empty(), Optional.empty(), RECEIVED_AT, 1));
    assertThrows(
        NullPointerException.class,
        () -> new RequestContext(MESSAGE_ID, MESSAGE_ID, null, Optional.empty(), RECEIVED_AT, 1));
    assertThrows(
        NullPointerException.class,
        () -> new RequestContext(MESSAGE_ID, MESSAGE_ID, Optional.empty(), null, RECEIVED_AT, 1));
    assertThrows(
        NullPointerException.class,
        () ->
            new RequestContext(
                MESSAGE_ID, MESSAGE_ID, Optional.empty(), Optional.empty(), null, 1));
    assertEquals(
        "root request identity is inconsistent",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new RequestContext(
                        MESSAGE_ID,
                        HTTP_REQUEST_ID,
                        Optional.empty(),
                        Optional.empty(),
                        RECEIVED_AT,
                        1))
            .getMessage());
  }

  @Test
  @DisplayName("PT-JMS-HCTX004 delivery count remains a positive int and part of identity")
  void retainsBoundaryCountsAndValueEquality() {
    for (int invalid : new int[] {0, -1, Integer.MIN_VALUE}) {
      assertEquals(
          "delivery count must be positive",
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new RequestContext(
                          MESSAGE_ID,
                          MESSAGE_ID,
                          Optional.empty(),
                          Optional.empty(),
                          RECEIVED_AT,
                          invalid))
              .getMessage());
    }
    var maximum =
        new RequestContext(
            MESSAGE_ID,
            MESSAGE_ID,
            Optional.empty(),
            Optional.empty(),
            RECEIVED_AT,
            Integer.MAX_VALUE);
    var equivalent =
        new RequestContext(
            MESSAGE_ID,
            MESSAGE_ID,
            Optional.empty(),
            Optional.empty(),
            RECEIVED_AT,
            Integer.MAX_VALUE);
    var first =
        new RequestContext(
            MESSAGE_ID, MESSAGE_ID, Optional.empty(), Optional.empty(), RECEIVED_AT, 1);
    assertEquals(Integer.MAX_VALUE, maximum.deliveryCount());
    assertEquals(maximum, equivalent);
    assertEquals(maximum.hashCode(), equivalent.hashCode());
    assertNotEquals(first, maximum);
  }

  @Test
  @DisplayName("PT-JMS-HCTX005 layout handler exposes the three typed operations")
  void exposesTheExpectedTypedBoundary() {
    var layout = new LayoutId("GAMREQ01");
    LayoutHandler<GameListRequestData, Integer> fixture =
        new LayoutHandler<>() {
          @Override
          public LayoutId requestLayout() {
            return layout;
          }

          @Override
          public Class<GameListRequestData> requestType() {
            return GameListRequestData.class;
          }

          @Override
          public Integer handle(RequestContext context, GameListRequestData request) {
            return context.deliveryCount();
          }
        };
    assertEquals(layout, fixture.requestLayout());
    assertEquals(GameListRequestData.class, fixture.requestType());
    assertEquals(
        3,
        fixture.handle(
            new RequestContext(
                MESSAGE_ID, MESSAGE_ID, Optional.empty(), Optional.empty(), RECEIVED_AT, 3),
            new GameListRequestData()));
    assertEquals(
        Set.of("requestLayout", "requestType", "handle"),
        Arrays.stream(LayoutHandler.class.getDeclaredMethods())
            .map(Method::getName)
            .collect(Collectors.toSet()));
  }
}
