package dev.codex.schubert.nk.web.error;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.view.ErrorViewModel;
import dev.codex.schubert.nk.web.view.ErrorViewModel.Status;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-WEB-001/SCR090; UI222 section7, SS313 section9; ERROR-VALUE001..006. */
final class ErrorValueContractTest {
  private static final UUID REQUEST = new UUID(0, 73);
  private static final Status[] STATUSES = {
    Status.BAD_REQUEST,
    Status.UNAUTHENTICATED,
    Status.FORBIDDEN,
    Status.NOT_FOUND,
    Status.METHOD_NOT_ALLOWED,
    Status.CONFLICT,
    Status.RANGE_INVALID,
    Status.RATE_LIMITED,
    Status.UNAVAILABLE
  };
  private static final int[] HTTP = {400, 401, 403, 404, 405, 409, 416, 429, 503};

  @Test
  void errorValue001AllTwelveResultCodesHaveIndependentHttpClassification() {
    ResultCode[] codes = {
      ResultCode.SUCCESS,
      ResultCode.VALIDATION_ERROR,
      ResultCode.AUTHENTICATION_FAILED,
      ResultCode.SESSION_INVALID,
      ResultCode.FORBIDDEN,
      ResultCode.NOT_FOUND,
      ResultCode.CONFLICT,
      ResultCode.LOCKED,
      ResultCode.NOT_CANCELLABLE,
      ResultCode.IDEMPOTENT_SUCCESS,
      ResultCode.TEMPORARY_FAILURE,
      ResultCode.RESOURCE_LIMIT
    };
    int[] expected = {200, 400, 401, 401, 403, 404, 409, 429, 409, 200, 503, 503};
    var mapper = new WebResultMapper();
    assertEquals(12, ResultCode.values().length);
    for (int i = 0; i < codes.length; i++) assertEquals(expected[i], mapper.httpStatus(codes[i]));
  }

  @Test
  void errorValue002ClassificationRejectsMissingResultCode() {
    assertEquals(
        "code",
        assertThrows(NullPointerException.class, () -> new WebResultMapper().httpStatus(null))
            .getMessage());
  }

  @Test
  void errorValue003FactoryUsesNineFixedStatusesAndMissingStatusMeans404() {
    var factory = new ProblemViewFactory();
    for (int code : HTTP) {
      var page = factory.create(code, REQUEST, Optional.empty());
      assertEquals(code, page.getStatus());
      assertEquals("00000000-0000-0000-0000-000000000049", page.getRequestId());
      assertTrue(page.getTopBar().isEmpty());
    }
    assertEquals(404, factory.create(null, REQUEST, Optional.empty()).getStatus());
  }

  @Test
  void errorValue004ForeignAndUnknownStatusRemain503WithoutNumericStringConversion() {
    var factory = new ProblemViewFactory();
    for (Object raw :
        List.of(
            0,
            200,
            500,
            Integer.MIN_VALUE,
            Integer.MAX_VALUE,
            "404",
            404L,
            new StringBuilder("404"),
            Boolean.TRUE)) {
      var page = factory.create(raw, REQUEST, Optional.empty());
      assertEquals(503, page.getStatus());
      assertEquals("現在処理できません。しばらくしてから再操作してください。", page.getMessage());
    }
  }

  @Test
  void errorValue005EveryClosedDisplayHasOnlyPublicRequestIdAndApprovedMessagePurpose() {
    String[] purpose = {"入力", "ログイン", "権限", "見つかりません", "操作方法", "再表示", "範囲", "しばらく", "再操作"};
    for (int i = 0; i < STATUSES.length; i++) {
      var page = ErrorViewModel.of(STATUSES[i], REQUEST, Optional.empty());
      assertEquals(HTTP[i], page.getStatus());
      assertTrue(page.getMessage().contains(purpose[i]));
      assertFalse(page.getMessage().isBlank());
      assertFalse(page.getMessage().contains("\n"));
      assertFalse(page.getMessage().contains("\r"));
      assertEquals("00000000-0000-0000-0000-000000000049", page.getRequestId());
      assertTrue(page.getTopBar().isEmpty());
      assertEquals("ErrorViewModel[REDACTED]", page.toString());
    }
    assertEquals(
        "この操作を実行する権限がありません。",
        ErrorViewModel.of(Status.FORBIDDEN, REQUEST, Optional.empty()).getMessage());
    assertEquals(
        "対象が見つかりません。", ErrorViewModel.of(Status.NOT_FOUND, REQUEST, Optional.empty()).getMessage());
    assertEquals(
        "状態が更新されたため操作できません。再表示してください。",
        ErrorViewModel.of(Status.CONFLICT, REQUEST, Optional.empty()).getMessage());
    assertEquals(
        "現在処理できません。しばらくしてから再操作してください。",
        ErrorViewModel.of(Status.UNAVAILABLE, REQUEST, Optional.empty()).getMessage());
  }

  @Test
  void errorValue006RequiredValuesRejectNullAndOptionalDisplaySnapshotIsRetained() {
    assertThrows(
        NullPointerException.class, () -> ErrorViewModel.of(null, REQUEST, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> ErrorViewModel.of(Status.NOT_FOUND, null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> ErrorViewModel.of(Status.NOT_FOUND, REQUEST, null));
    var factory = new ProblemViewFactory();
    assertThrows(NullPointerException.class, () -> factory.create(null, null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> factory.create(null, REQUEST, null));
    var bar =
        TopBarViewModel.from(
            new SessionPrincipal(
                "PUBLIC_DISPLAY",
                UserRole.USER,
                AuthenticationContext.of("a".repeat(64)),
                Instant.parse("2026-11-01T00:00:00Z")));
    var selected = Optional.of(bar);
    var direct = ErrorViewModel.of(Status.NOT_FOUND, REQUEST, selected);
    assertSame(selected, direct.getTopBar());
    assertSame(bar, direct.getTopBar().orElseThrow());
    assertSame(selected, factory.create(404, REQUEST, selected).getTopBar());
    assertEquals("PUBLIC_DISPLAY", bar.getUsername());
    assertEquals("USER", bar.getRole());
  }
}
