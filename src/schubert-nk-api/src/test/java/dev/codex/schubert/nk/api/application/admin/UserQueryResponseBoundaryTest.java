package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * UI236 literal bytes and SS323 §9.4 response invariants, without DB/crypto/worker fixtures.
 * NK-ADM-001; WBS-P010-01; PT-ADM-VAL001..004; BUG1781/YKT1532; specification 2008.
 */
class UserQueryResponseBoundaryTest {
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String SEARCH_RESPONSE = "USRRSP01";
  private static final String DETAIL_LAYOUT = "UDTREQ01";
  private static final String DETAIL_RESPONSE = "UDTRSP01";
  private static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");

  @Test
  void val001LiteralSearchAndEmptyResponseHonorInterfaceConstants() {
    byte[] data = searchBytes();
    var wire = wire(SEARCH_LAYOUT, data);
    var request = UserQueryRequest.decode(wire);
    assertFalse(request.detailRequest());
    assertEquals(SEARCH_RESPONSE, request.responseLayoutId().value());
    assertEquals(wire.header(), request.header());
    assertArrayEquals(data, wire.payload().copyData());
    var response = page(new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
    assertDoesNotThrow(() -> request.validateResponse(response));
  }

  @Test
  void val002PageIdentityAndSizeRejectTypedFailures() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes()));
    var wrongPage = page(new PagedResponseData(0, 50, 0, 1, 0, 0), List.of());
    var wrongSize = page(new PagedResponseData(1, 49, 0, 1, 0, 0), List.of());
    assertThrows(IllegalArgumentException.class, () -> request.validateResponse(wrongPage));
    assertThrows(LayoutValidationException.class, () -> request.validateResponse(wrongSize));
    // Null is a separate declared API-boundary rejection, not an acceptable page failure.
    assertThrows(NullPointerException.class, () -> request.validateResponse(null));
  }

  @Test
  void val003RecordCountsAndPaginationCannotDisagree() {
    var request = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes()));
    List<PayloadRecord> oneRow =
        List.of(
            new UserRecord(
                new UserId(1),
                "u1",
                UserRole.USER,
                UserState.ACTIVE,
                Optional.empty(),
                Optional.empty(),
                NOW,
                NOW,
                0));
    var extraRow = page(new PagedResponseData(1, 50, 0, 1, 0, 0), oneRow);
    var missingRow = page(new PagedResponseData(1, 50, 1, 1, 1, 1), List.of());
    var correct = page(new PagedResponseData(1, 50, 1, 1, 1, 1), oneRow);
    assertThrows(LayoutValidationException.class, () -> request.validateResponse(extraRow));
    assertThrows(LayoutValidationException.class, () -> request.validateResponse(missingRow));
    assertDoesNotThrow(() -> request.validateResponse(correct));
    assertEquals(1, correct.records().size());
    assertEquals(1, ((UserRecord) correct.records().getFirst()).userId().value());
  }

  @Test
  void val004LayoutDataAndDetailTargetAreBoundToOriginalRequest() {
    var detail =
        UserQueryRequest.decode(
            wire(DETAIL_LAYOUT, "000000000003".getBytes(StandardCharsets.US_ASCII)));
    var search = UserQueryRequest.decode(wire(SEARCH_LAYOUT, searchBytes()));
    assertTrue(detail.detailRequest());
    assertEquals(DETAIL_RESPONSE, detail.responseLayoutId().value());
    var correct = detailResponse(3);
    var wrongTarget = detailResponse(4);
    var wrongLayout = page(new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
    var wrongType =
        new TypedPayloadValues(new LayoutId(SEARCH_RESPONSE), correct.data(), List.of());
    assertDoesNotThrow(() -> detail.validateResponse(correct));
    assertThrows(IllegalArgumentException.class, () -> detail.validateResponse(wrongTarget));
    assertThrows(IllegalArgumentException.class, () -> detail.validateResponse(wrongLayout));
    assertThrows(IllegalArgumentException.class, () -> search.validateResponse(correct));
    assertThrows(IllegalArgumentException.class, () -> search.validateResponse(wrongType));
  }

  private static byte[] searchBytes() {
    // UI236: 96 space bytes; page starts at byte78, fixed page size50 at byte84.
    byte[] data = new byte[96];
    Arrays.fill(data, (byte) 32);
    byte[] pageAndSize = "000001050".getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(pageAndSize, 0, data, 77, pageAndSize.length);
    return data;
  }

  private static WireMessage<FixedPayload> wire(String layout, byte[] data) {
    // A synthetic format-only context; no authentication, credential lookup or connection.
    UUID message = new UUID(2008, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            message,
            message,
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

  private static TypedPayloadValues page(PagedResponseData data, List<PayloadRecord> records) {
    return new TypedPayloadValues(new LayoutId(SEARCH_RESPONSE), data, records);
  }

  private static TypedPayloadValues detailResponse(long target) {
    var data =
        new UserDetailResponseData(
            new UserId(target),
            "u3",
            UserRole.USER,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.empty(),
            NOW,
            NOW,
            NOW,
            0,
            0,
            "SYSTEM",
            "SYSTEM");
    return new TypedPayloadValues(new LayoutId(DETAIL_RESPONSE), data, List.of());
  }
}
