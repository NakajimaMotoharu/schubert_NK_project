package dev.codex.schubert.nk.api.application.log;

import static dev.codex.schubert.nk.api.application.log.LogVectors.ADMIN;
import static dev.codex.schubert.nk.api.application.log.LogVectors.MESSAGE;
import static dev.codex.schubert.nk.api.application.log.LogVectors.NOW;
import static dev.codex.schubert.nk.api.application.log.LogVectors.check;
import static dev.codex.schubert.nk.api.application.log.LogVectors.data;
import static dev.codex.schubert.nk.api.application.log.LogVectors.emptyFilters;
import static dev.codex.schubert.nk.api.application.log.LogVectors.message;
import static dev.codex.schubert.nk.api.application.log.LogVectors.page;
import static dev.codex.schubert.nk.api.application.log.LogVectors.put;
import static dev.codex.schubert.nk.api.application.log.LogVectors.request;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.persistence.LogQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** UI235 and SSC037 independent input/LP/SQL expectations, PT-ADM-061..063. */
class LogRequestTest {
  // Test-local UI235 literal, independent of all Production layout constants.
  private static final String SEARCH_LAYOUT = "LGSREQ01";
  @TempDir Path root;

  @Test
  void adm061CanonicalPreservesEveryOriginalFilterAndDate() throws Exception {
    var all =
        List.of(
            " É_%\\'",
            "SECURITY", "Exact", "/safe", "WARN", NOW.toString(), NOW.plusMillis(1).toString());
    for (int mask = 0; mask < 128; mask++) {
      var fields = new ArrayList<String>();
      for (int i = 0; i < 7; i++) fields.add((mask & (1 << i)) == 0 ? null : all.get(i));
      for (int page : new int[] {1, 999999})
        check(request(fields, page, MESSAGE), ADMIN, fields, page);
    }
    for (String keyword : List.of("é".repeat(128), "lower", "LOWER", " e\u0301")) {
      var fields = new ArrayList<>(emptyFilters());
      fields.set(0, keyword);
      var expected = new ArrayList<>(fields);
      expected.set(0, java.text.Normalizer.normalize(keyword, java.text.Normalizer.Form.NFC));
      check(request(fields, 1, MESSAGE), ADMIN, expected, 1);
    }
    var wire = message(SEARCH_LAYOUT, data(emptyFilters(), 1), MESSAGE);
    var decoded = LogRequest.decode(wire);
    assertSame(wire.header(), decoded.header());
    assertEquals("LGSRSP01", decoded.responseLayoutId().value());
    assertEquals("LogRequest[REDACTED]", decoded.toString());
    assertArrayEquals(
        check(decoded, ADMIN, emptyFilters(), 1),
        check(request(emptyFilters(), 1, new UUID(200, 2)), ADMIN, emptyFilters(), 1));
    var changed = new ArrayList<>(emptyFilters());
    changed.set(0, "LOWER");
    byte[] upper = check(request(changed, 1, MESSAGE), ADMIN, changed, 1);
    changed.set(0, "lower");
    assertFalse(Arrays.equals(upper, check(request(changed, 1, MESSAGE), ADMIN, changed, 1)));
  }

  @Test
  void adm062StrictBoundariesAndRealQueryUseOneDecodedRequest() throws Exception {
    var request = request(1);
    var repo = new LogQueryRepository();
    assertThrows(NullPointerException.class, () -> LogRequest.decode(null));
    assertThrows(NullPointerException.class, () -> request.canonical(null));
    assertThrows(NullPointerException.class, () -> request.validateResponse(null));
    invalid(
        message(
            "UDTREQ01",
            "000000000001".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
            MESSAGE));
    for (byte[] bytes : List.of(new byte[655], new byte[657], new byte[656]))
      invalid(message(SEARCH_LAYOUT, bytes, MESSAGE));
    for (var change :
        Map.of(
                256,
                "UNKNOWN",
                592,
                "TRACE",
                600,
                "20261301000000000",
                634,
                "000000",
                640,
                "099",
                643,
                "x")
            .entrySet()) {
      byte[] bytes = data(emptyFilters(), 1);
      put(bytes, change.getKey(), change.getValue());
      invalid(message(SEARCH_LAYOUT, bytes, MESSAGE));
    }
    for (var dates :
        List.of(
            List.of(NOW.plusMillis(1).toString(), NOW.toString()),
            List.of(NOW.toString(), NOW.plusSeconds(31 * 86400L).plusMillis(1).toString()))) {
      var fields = new ArrayList<>(emptyFilters());
      fields.set(5, dates.get(0));
      fields.set(6, dates.get(1));
      invalid(message(SEARCH_LAYOUT, data(fields, 1), MESSAGE));
    }
    for (int mode = 0; mode < 3; mode++) {
      int records = mode == 2 ? 1 : 0;
      var header =
          new CommonHeader(
              "SCHBNK01",
              1,
              new LayoutId(SEARCH_LAYOUT),
              1,
              mode == 0 ? MessageKind.RESPONSE : MessageKind.REQUEST,
              mode == 1 ? InteractionKind.ASYNC_ACCEPTANCE : InteractionKind.SYNCHRONOUS,
              MESSAGE,
              MESSAGE,
              NOW,
              Optional.of(AuthenticationContext.of("b".repeat(64))),
              256,
              656,
              records,
              records,
              912 + records,
              mode == 0 ? Optional.of(ResultCode.SUCCESS) : Optional.empty());
      invalid(
          new WireMessage<>(
              header,
              new FixedPayload(
                  data(emptyFilters(), 1),
                  records,
                  records == 0 ? List.of() : List.of(new byte[] {32}))));
    }
    request.validateResponse(page(0, 0, 1, false));
    request(999999).validateResponse(page(1, 101, 2, true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request.validateResponse(
                new TypedPayloadValues(
                    new LayoutId("USRRSP01"),
                    new PagedResponseData(1, 50, 0, 1, 0, 0),
                    List.of())));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request.validateResponse(
                new TypedPayloadValues(
                    new LayoutId("LGSRSP01"),
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
                    List.of())));
    assertThrows(
        IllegalArgumentException.class, () -> request.validateResponse(page(1, 101, 2, false)));
    assertThrows(
        IllegalArgumentException.class, () -> request.validateResponse(page(1, 2, 1, false)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request.validateResponse(
                new TypedPayloadValues(
                    new LayoutId("LGSRSP01"),
                    new PagedResponseData(1, 99, 0, 1, 0, 0),
                    List.of())));
    var db = new ApiLogDatabaseFixture(root);
    try {
      try (var admin = db.admin();
          var sql = admin.createStatement()) {
        sql.executeUpdate(
            "insert into schubert.app_logs(logged_at,service,category,level,action,message,details)"
                + " values ('2026-09-08T00:00:00Z','API','SECURITY','WARN','Exact','É_%',"
                + " '{}'::jsonb)");
      }
      try (var c = db.transaction()) {
        c.setReadOnly(true);
        var filters =
            Arrays.asList(
                " É_%", "SECURITY", "Exact", null, "WARN", NOW.toString(), NOW.toString());
        var decoded = request(filters, 999999, MESSAGE);
        var response = decoded.query(repo, c, ADMIN);
        decoded.validateResponse(response);
        assertEquals(new PagedResponseData(1, 100, 1, 1, 1, 1), response.data());
        assertEquals(1, response.records().size());
        var row = (LogRecord) response.records().getFirst();
        assertEquals(1, row.logId().value());
        assertEquals("É_%", row.message());
        assertEquals("{}", row.details().orElseThrow());
        assertFalse(c.getAutoCommit());
        assertTrue(c.isReadOnly());
        assertFalse(c.isClosed());
        assertThrows(NullPointerException.class, () -> request.query(null, c, ADMIN));
        assertThrows(NullPointerException.class, () -> request.query(repo, null, ADMIN));
        assertThrows(NullPointerException.class, () -> request.query(repo, c, null));
        var denied =
            assertThrows(
                dev.codex.schubert.nk.api.security.AuthorizationException.class,
                () -> request.query(repo, c, new AuthenticatedActor(2, "user", Role.USER)));
        assertEquals(ResultCode.FORBIDDEN, denied.resultCode());
        assertNull(denied.getCause());
        c.commit();
      }
      try (var c = db.api()) {
        assertThrows(
            dev.codex.schubert.nk.api.persistence.LogQueryException.class,
            () -> request.query(repo, c, ADMIN));
      }
      try (var c = db.transaction()) {
        assertThrows(
            dev.codex.schubert.nk.api.persistence.LogQueryException.class,
            () -> request.query(repo, c, ADMIN));
      }
      try (var c = db.api();
          var sql = c.createStatement();
          var rows = sql.executeQuery("select count(*) from schubert.app_logs")) {
        assertTrue(rows.next());
        assertEquals(1, rows.getInt(1));
        assertFalse(rows.next());
      }
    } finally {
      db.stop();
    }
  }

  @Test
  void adm063ConcurrentCanonicalBuffersRemainIndependent() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      var results = new ArrayList<Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        final int n = i;
        results.add(
            pool.submit(
                () -> {
                  var actor = new AuthenticatedActor(n, "admin" + n, Role.ADMIN);
                  var filters =
                      Arrays.asList(
                          "q" + n, null, null, "/" + n, null, NOW.plusMillis(n).toString(), null);
                  var request = request(filters, n, new UUID(200, n));
                  check(request, actor, filters, n);
                  var first = request.canonical(actor);
                  try (var second = request.canonical(actor);
                      var keys = new FingerprintKeyRing("test", new byte[32], null, null)) {
                    byte[] expected = keys.calculate(second).digest();
                    first.close();
                    for (var field : first.fields())
                      if (field.value() != null)
                        assertArrayEquals(new byte[field.value().length], field.value());
                    assertArrayEquals(expected, keys.calculate(second).digest());
                    check(request, actor, filters, n);
                  } finally {
                    first.close();
                  }
                  return null;
                }));
      }
      for (var result : results) result.get(20, TimeUnit.SECONDS);
    }
  }

  static void invalid(WireMessage<FixedPayload> message) {
    var e = assertThrows(PermanentProtocolException.class, () -> LogRequest.decode(message));
    assertEquals("log request is invalid", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }
}
