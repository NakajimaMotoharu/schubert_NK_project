package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/**
 * SS323 independent literal31; PT-JMS-DISPATCH-026-A..F. Marker-only dispatcher PT, not business
 * readiness or native registration evidence.
 */
final class ApiSyncRequestDispatcherTest {
  private static final List<String> IDS =
      List.of(
          "LGNREQ01",
          "LOGREQ01",
          "GAMREQ01",
          "SPKREQ01",
          "SRCREQ01",
          "RTEREQ01",
          "SCFREQ01",
          "SCNREQ01",
          "AUDREQ01",
          "ANMREQ01",
          "ANLREQ01",
          "VIDREQ01",
          "MCTREQ01",
          "MCSREQ01",
          "MTRREQ01",
          "MEDREQ01",
          "LGSREQ01",
          "USRREQ01",
          "UDTREQ01",
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTSREQ01",
          "NTDREQ01",
          "NTCREQ01",
          "QSSREQ01",
          "QSDREQ01",
          "QDLREQ01");

  static Map<String, SyncRequestProcessor> registrations() {
    var result = new HashMap<String, SyncRequestProcessor>();
    for (String id : IDS)
      result.put(
          id,
          request -> {
            assertEquals(id, request.header().layoutId().value());
            return id.getBytes(StandardCharsets.US_ASCII);
          });
    return result;
  }

  @Test
  void everyLiteralRequestReachesExactlyItsOwnProcessorAndMapCopyIsImmutable() throws Exception {
    var input = registrations();
    var router = new ApiSyncRequestDispatcher(input);
    input.clear();
    assertEquals(31, IDS.size());
    for (String id : IDS)
      assertArrayEquals(id.getBytes(StandardCharsets.US_ASCII), router.process(request(id)));
  }

  @Test
  void eachMissingUnexpectedAndWrongRouteFailsBeforeRegistration() {
    for (String id : IDS) {
      var input = registrations();
      input.remove(id);
      assertThrows(IOException.class, () -> new ApiSyncRequestDispatcher(input));
    }
    for (String id : List.of("LGNRSP01", "WLGEVT01", "QWKREQ01", "ZZZREQ01", "")) {
      var input = registrations();
      input.put(id, r -> new byte[0]);
      assertThrows(IOException.class, () -> new ApiSyncRequestDispatcher(input));
    }
    assertThrows(IOException.class, () -> new ApiSyncRequestDispatcher(Map.of()));
  }

  @Test
  void nullBoundaryAndDelegateNullRejectWithoutSuccess() throws Exception {
    assertThrows(NullPointerException.class, () -> new ApiSyncRequestDispatcher(null));
    var input = registrations();
    input.put("LGNREQ01", null);
    assertThrows(NullPointerException.class, () -> new ApiSyncRequestDispatcher(input));
    var nullKey = registrations();
    nullKey.put(null, r -> new byte[0]);
    assertThrows(NullPointerException.class, () -> new ApiSyncRequestDispatcher(nullKey));
    var delegates = registrations();
    delegates.put("LGNREQ01", r -> null);
    var router = new ApiSyncRequestDispatcher(delegates);
    assertThrows(NullPointerException.class, () -> router.process(null));
    assertThrows(NullPointerException.class, () -> router.process(request("LGNREQ01")));
  }

  @Test
  void validResponseOrInternalRouteCannotBeConsumedAsRequest() throws Exception {
    var router = new ApiSyncRequestDispatcher(registrations());
    for (String id : List.of("LGNRSP01", "WLGEVT01", "QWKREQ01", "ZZZREQ01"))
      assertThrows(TemporaryInfrastructureException.class, () -> router.process(request(id)));
  }

  @Test
  void delegateUnknownAndFatalIdentityArePreserved() throws Exception {
    var input = registrations();
    var failure = new IllegalStateException("public fixture");
    var fatal = new AssertionError("public fatal");
    input.put(
        "LGNREQ01",
        r -> {
          throw failure;
        });
    input.put(
        "LOGREQ01",
        r -> {
          throw fatal;
        });
    var router = new ApiSyncRequestDispatcher(input);
    assertSame(
        failure,
        assertThrows(IllegalStateException.class, () -> router.process(request("LGNREQ01"))));
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> router.process(request("LOGREQ01"))));
  }

  @Test
  void parallelDispatchDoesNotShareSelection() throws Exception {
    var router = new ApiSyncRequestDispatcher(registrations());
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var futures = new ArrayList<java.util.concurrent.Future<byte[]>>();
      for (String id : IDS) futures.add(executor.submit(() -> router.process(request(id))));
      for (int i = 0; i < IDS.size(); i++)
        assertArrayEquals(IDS.get(i).getBytes(StandardCharsets.US_ASCII), futures.get(i).get());
    }
  }

  static WireMessage<FixedPayload> request(String id) {
    var message = new UUID(0, 1);
    boolean event = Set.of("WLGEVT01", "QWKREQ01").contains(id);
    boolean response = id.equals("LGNRSP01");
    var kind = event ? MessageKind.EVENT : response ? MessageKind.RESPONSE : MessageKind.REQUEST;
    var context =
        event || Set.of("LGNREQ01", "LGNRSP01").contains(id)
            ? Optional.<AuthenticationContext>empty()
            : Optional.of(AuthenticationContext.of("a".repeat(64)));
    return new WireMessage<>(
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(id),
            1,
            kind,
            event
                ? InteractionKind.INTERNAL
                : id.equals("QSBREQ01")
                    ? InteractionKind.ASYNC_ACCEPTANCE
                    : InteractionKind.SYNCHRONOUS,
            message,
            message,
            Instant.parse("2026-09-24T00:00:00Z"),
            context,
            256,
            0,
            0,
            0,
            256,
            response ? Optional.of(ResultCode.SUCCESS) : Optional.empty()),
        new FixedPayload(new byte[0], 0, List.of()));
  }
}
