package dev.codex.schubert.nk.api.application.log;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** UI235/SS323 §9.5; NK-ADM-001; WBS-P018-09; PT-LOG-PLAIN001..008; spec2016. */
class LogPlainContractTest {
  private static final String SEARCH = "LGSREQ01";
  private static final String RESPONSE = "LGSRSP01";
  private static final Instant NOW = Instant.parse("2026-10-01T00:00:00.123Z");
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(8, "unit8", Role.ADMIN);
  private static final List<String> NAMES =
      List.of("keyword", "logType", "action", "path", "level", "fromAt", "toAt");
  private static final List<String> TYPES = List.of("X1", "X1", "X1", "X1", "X1", "T1", "T1");
  private static final List<String> VALUES =
      List.of(
          "é_%",
          "SECURITY",
          "Read",
          "/plain",
          "WARN",
          "2026-10-01T00:00:00.123Z",
          "2026-10-01T00:00:01.123Z");
  private static final int[] OFFSETS = {0, 256, 272, 336, 592, 600, 617};
  private static final List<String> WIRE_VALUES =
      List.of(
          "é_%", "SECURITY", "Read", "/plain", "WARN", "20261001090000123", "20261001090001123");

  @Test
  void plain001AbsentFieldsAndOriginalPageHaveLiteralMetadata() {
    var wire = wire(SEARCH, data(0, 999999));
    var request = LogRequest.decode(wire);
    assertSame(wire.header(), request.header());
    assertEquals(RESPONSE, request.responseLayoutId().value());
    assertEquals("LogRequest[REDACTED]", request.toString());
    try (var canonical = request.canonical(ACTOR)) {
      assertEquals("8", canonical.ownerScope());
      assertEquals(SEARCH, canonical.layoutId());
      assertEquals("001", canonical.layoutVersion());
      assertEquals("REQUEST:LGSREQ01", canonical.target());
      assertEquals(9, canonical.fields().size());
      for (int i = 0; i < 7; i++) {
        assertEquals(NAMES.get(i), canonical.fields().get(i).name());
        assertEquals(TYPES.get(i), canonical.fields().get(i).typeVersion());
        assertNull(canonical.fields().get(i).value());
      }
      assertEquals("page", canonical.fields().get(7).name());
      assertEquals("pageSize", canonical.fields().get(8).name());
      assertEquals("N1", canonical.fields().get(7).typeVersion());
      assertEquals("N1", canonical.fields().get(8).typeVersion());
      assertArrayEquals(
          "999999".getBytes(StandardCharsets.US_ASCII), canonical.fields().get(7).value());
      assertArrayEquals(
          "100".getBytes(StandardCharsets.US_ASCII), canonical.fields().get(8).value());
    }
  }

  @Test
  void plain002FilledFieldsPreserveUtf8OriginalFiltersAndUtcDates() {
    var request = LogRequest.decode(wire(SEARCH, data(127, 1)));
    try (var canonical = request.canonical(ACTOR)) {
      for (int i = 0; i < 7; i++) {
        assertEquals(NAMES.get(i), canonical.fields().get(i).name());
        assertEquals(TYPES.get(i), canonical.fields().get(i).typeVersion());
        assertArrayEquals(
            VALUES.get(i).getBytes(StandardCharsets.UTF_8), canonical.fields().get(i).value());
      }
      assertArrayEquals("1".getBytes(StandardCharsets.US_ASCII), canonical.fields().get(7).value());
    }
  }

  @Test
  void plain003MalformedLayoutLengthEnumDatesAndReservedAreRejected() {
    var failure =
        assertThrows(
            PermanentProtocolException.class,
            () -> LogRequest.decode(wire("ZZZREQ01", data(0, 1))));
    assertEquals("log request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    for (int length : new int[] {655, 657}) {
      byte[] bytes = Arrays.copyOf(data(0, 1), length);
      assertThrows(PermanentProtocolException.class, () -> LogRequest.decode(wire(SEARCH, bytes)));
    }
    for (int index = 0; index < 5; index++) {
      byte[] bad = data(0, 1);
      switch (index) {
        case 0 -> put(bad, 256, "UNKNOWN");
        case 1 -> put(bad, 592, "TRACE");
        case 2 -> put(bad, 600, "20261301000000000");
        case 3 -> put(bad, 634, "000000");
        default -> bad[643] = 'x';
      }
      assertThrows(PermanentProtocolException.class, () -> LogRequest.decode(wire(SEARCH, bad)));
    }
  }

  @Test
  void plain004NullPublicBoundariesStopBeforeAnyRepositoryReceiver() {
    var request = LogRequest.decode(wire(SEARCH, data(0, 1)));
    assertThrows(NullPointerException.class, () -> LogRequest.decode(null));
    assertThrows(NullPointerException.class, () -> request.canonical(null));
    assertThrows(NullPointerException.class, () -> request.query(null, null, null));
    assertThrows(NullPointerException.class, () -> request.validateResponse(null));
  }

  @Test
  void plain005EmptyResponseClampsRequestedPageWithoutChangingCanonicalPage() {
    var request = LogRequest.decode(wire(SEARCH, data(0, 999999)));
    assertDoesNotThrow(() -> request.validateResponse(page(1, 100, 0)));
    try (var canonical = request.canonical(ACTOR)) {
      assertArrayEquals(
          "999999".getBytes(StandardCharsets.US_ASCII), canonical.fields().get(7).value());
    }
  }

  @Test
  void plain006WrongPageSizeAndRecordCountNeverAcceptNpeAsSuccess() {
    var request = LogRequest.decode(wire(SEARCH, data(0, 1)));
    assertThrows(IllegalArgumentException.class, () -> request.validateResponse(page(0, 100, 0)));
    assertThrows(LayoutValidationException.class, () -> request.validateResponse(page(1, 99, 0)));
    assertThrows(LayoutValidationException.class, () -> request.validateResponse(page(1, 100, 1)));
  }

  @Test
  void plain007WrongResponseLayoutAndNonPagedDataAreRejected() {
    var request = LogRequest.decode(wire(SEARCH, data(0, 1)));
    var wrongLayout =
        new TypedPayloadValues(
            new LayoutId("USRRSP01"), new PagedResponseData(1, 100, 0, 1, 0, 0), List.of());
    var wrongData =
        new TypedPayloadValues(
            new LayoutId(RESPONSE),
            new LogSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                1,
                100),
            List.of());
    assertThrows(IllegalArgumentException.class, () -> request.validateResponse(wrongLayout));
    assertThrows(IllegalArgumentException.class, () -> request.validateResponse(wrongData));
  }

  @Test
  void plain008AllSevenOptionalPresenceMasksUseIndependentExpectedValues() {
    for (int mask = 0; mask < 128; mask++) {
      var request = LogRequest.decode(wire(SEARCH, data(mask, 1)));
      try (var canonical = request.canonical(ACTOR)) {
        assertEquals(9, canonical.fields().size());
        for (int i = 0; i < 7; i++) {
          assertEquals(NAMES.get(i), canonical.fields().get(i).name());
          assertEquals(TYPES.get(i), canonical.fields().get(i).typeVersion());
          if ((mask & (1 << i)) == 0) {
            assertNull(canonical.fields().get(i).value());
          } else {
            assertArrayEquals(
                VALUES.get(i).getBytes(StandardCharsets.UTF_8), canonical.fields().get(i).value());
          }
        }
      }
    }
  }

  private static TypedPayloadValues page(int effective, int size, int count) {
    return new TypedPayloadValues(
        new LayoutId(RESPONSE),
        new PagedResponseData(effective, size, count, 1, count, count),
        List.of());
  }

  private static byte[] data(int mask, int page) {
    byte[] bytes = new byte[656];
    Arrays.fill(bytes, (byte) 32);
    for (int i = 0; i < 7; i++) {
      if ((mask & (1 << i)) != 0) put(bytes, OFFSETS[i], WIRE_VALUES.get(i));
    }
    put(bytes, 634, page == 1 ? "000001100" : "999999100");
    return bytes;
  }

  private static void put(byte[] data, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, data, offset, bytes.length);
  }

  private static WireMessage<FixedPayload> wire(String layout, byte[] data) {
    UUID id = new UUID(2016, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }
}
