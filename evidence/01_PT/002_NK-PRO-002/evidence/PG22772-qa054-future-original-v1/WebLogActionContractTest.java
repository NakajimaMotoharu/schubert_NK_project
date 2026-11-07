package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.log.WebLogEventData;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.lang.reflect.InvocationTargetException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** UI235 §12.2 literal-byte oracle; QA054/SSC336, no backend or credential fixture. */
class WebLogActionContractTest {
  private static final Instant AT = Instant.parse("2026-11-05T00:00:00Z");
  private static final UUID ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final LayoutId LAYOUT = new LayoutId("WLGEVT01");
  private static final String REQUEST_CATEGORY = "REQUEST";
  private static final String ACTION_CATEGORY = "ACTION";
  private static final String GET_METHOD = "GET";
  private static final String USERNAME = "user";
  private static final String REQUEST_ACTION = "HTTP_REQUEST_COMPLETED";
  private static final String MENU_ACTION = "MENU_VIEWED";
  private static final String ADDRESS = "127.0.0.1";
  private static final String SAFE_MESSAGE = "safe menu";

  @Test // PT-PRO-QA054-001
  void legacyRequestMatchesIndependentOriginalBytes() {
    var value = legacy(Optional.empty());
    assertEquals(LogType.REQUEST, value.logType());
    assertArrayEquals(golden(REQUEST_CATEGORY, ""), encode(value));
    assertEquals(value, decode(golden(REQUEST_CATEGORY, "")));
    assertEquals(64, LayoutRegistry.standard().all().size());
    assertEquals(2336, LayoutRegistry.standard().require(LAYOUT, 1).maximumTotalLength());
    assertEquals(2080, encode(value).length);
  }

  @Test // PT-PRO-QA054-002
  void menuActionMatchesIndependentOffsetsAndRoundTrips() {
    var value = value(LogType.ACTION, Optional.of(MENU_ACTION));
    byte[] expected = golden(ACTION_CATEGORY, MENU_ACTION);
    assertArrayEquals(expected, encode(value));
    assertEquals(value, decode(expected));
    assertEquals("ACTION          ", new String(expected, 17, 16, StandardCharsets.US_ASCII));
    assertEquals(MENU_ACTION, new String(expected, 41, 64, StandardCharsets.US_ASCII).trim());
  }

  @Test // PT-PRO-QA054-003
  void explicitRequestActionKeepsItsOwnClosedPair() {
    assertArrayEquals(
        golden(REQUEST_CATEGORY, REQUEST_ACTION), encode(legacy(Optional.of(REQUEST_ACTION))));
    assertEquals(LogType.REQUEST, decode(golden(REQUEST_CATEGORY, REQUEST_ACTION)).logType());
    assertNotEquals(
        decode(golden(ACTION_CATEGORY, MENU_ACTION)), legacy(Optional.of(REQUEST_ACTION)));
  }

  @Test // PT-PRO-QA054-004
  void everyOtherCategoryIsRejectedByNamedBoundary() {
    for (LogType type : List.of(LogType.SECURITY, LogType.MQ, LogType.SYSTEM, LogType.BATCH)) {
      assertThrows(
          LayoutValidationException.class, () -> encode(value(type, Optional.of(MENU_ACTION))));
      assertThrows(LayoutValidationException.class, () -> decode(golden(type.name(), MENU_ACTION)));
    }
  }

  @Test // PT-PRO-QA054-005
  void crossedAndUnknownActionsAreNeverNormalizedToSuccess() {
    for (String action : List.of(REQUEST_ACTION, "LOG_SEARCHED", "UNKNOWN", "menu_viewed")) {
      assertThrows(LayoutValidationException.class, () -> decode(golden(ACTION_CATEGORY, action)));
    }
    for (String action : List.of(MENU_ACTION, "LOG_SEARCHED", "UNKNOWN")) {
      assertThrows(LayoutValidationException.class, () -> decode(golden(REQUEST_CATEGORY, action)));
    }
  }

  @Test // PT-PRO-QA054-006
  void omittedActionIsAllowedForRequestOnly() {
    assertEquals(Optional.empty(), decode(golden(REQUEST_CATEGORY, "")).action());
    assertThrows(LayoutValidationException.class, () -> decode(golden(ACTION_CATEGORY, "")));
    assertThrows(
        LayoutValidationException.class, () -> encode(value(LogType.ACTION, Optional.empty())));
  }

  @Test // PT-PRO-QA054-007
  void missingBlankUnknownAndWrongCaseCategoryFail() {
    assertThrows(PermanentProtocolException.class, () -> decode(golden("", REQUEST_ACTION)));
    for (String category : List.of("UNKNOWN", "request", "Action")) {
      assertThrows(LayoutValidationException.class, () -> decode(golden(category, MENU_ACTION)));
    }
    var fields = new LinkedHashMap<String, FieldValue>();
    var original = legacy(Optional.empty()).fields();
    for (String name : original.names()) fields.put(name, original.getOrUnset(name));
    fields.remove("Log type");
    assertThrows(
        LayoutValidationException.class, () -> WebLogEventData.from(new FieldValueSet(fields)));
  }

  @Test // PT-PRO-QA054-008
  void nfcAndExactUtf8ByteBoundaryHaveIndependentExpectedBytes() {
    var payload = legacy(Optional.empty());
    var fields = new LinkedHashMap<String, FieldValue>();
    for (String name : payload.fields().names())
      fields.put(name, payload.fields().getOrUnset(name));
    fields.put("Message", new FieldValue.Text("e\u0301"));
    byte[] actual =
        PayloadCodec.standard()
            .encode(new PayloadValues(LAYOUT, new FieldValueSet(fields), List.of()), false)
            .copyData();
    byte[] expected = golden(REQUEST_CATEGORY, "");
    Arrays.fill(expected, 105, 617, (byte) ' ');
    put(expected, 106, "é");
    assertArrayEquals(expected, actual);
    fields.put("Message", new FieldValue.Text("é".repeat(256)));
    assertEquals(
        2080,
        PayloadCodec.standard()
            .encode(new PayloadValues(LAYOUT, new FieldValueSet(fields), List.of()), false)
            .dataLength());
    fields.put("Message", new FieldValue.Text("é".repeat(256) + "a"));
    assertThrows(
        FieldEncodingException.class,
        () ->
            PayloadCodec.standard()
                .encode(new PayloadValues(LAYOUT, new FieldValueSet(fields), List.of()), false));
  }

  @Test // PT-PRO-QA054-009
  void everyCanonicalConstructorReferenceRejectsNull() throws Exception {
    var constructor =
        WebLogEventData.class.getDeclaredConstructor(
            Instant.class,
            LogType.class,
            LogLevel.class,
            Optional.class,
            String.class,
            UUID.class,
            String.class,
            String.class,
            HttpStatusCode.class,
            ElapsedMilliseconds.class,
            String.class,
            Optional.class,
            Optional.class,
            Optional.class);
    Object[] args = {
      AT,
      LogType.ACTION,
      LogLevel.INFO,
      Optional.of(MENU_ACTION),
      SAFE_MESSAGE,
      ID,
      GET_METHOD,
      "/",
      new HttpStatusCode(200),
      new ElapsedMilliseconds(12),
      ADDRESS,
      Optional.of(USERNAME),
      Optional.of(UserRole.USER),
      Optional.of("{}")
    };
    for (int i = 0; i < args.length; i++) {
      Object[] invalid = args.clone();
      invalid[i] = null;
      InvocationTargetException failure =
          assertThrows(InvocationTargetException.class, () -> constructor.newInstance(invalid));
      assertInstanceOf(NullPointerException.class, failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> WebLogEventData.from(null));
  }

  @Test // PT-PRO-QA054-010
  void existingHttpMetadataAndReservedRulesRemainEnforced() {
    for (String path : List.of("relative", "/?query")) {
      byte[] bytes = golden(ACTION_CATEGORY, MENU_ACTION);
      Arrays.fill(bytes, 661, 917, (byte) ' ');
      put(bytes, 662, path);
      assertThrows(LayoutValidationException.class, () -> decode(bytes));
    }
    byte[] method = golden(ACTION_CATEGORY, MENU_ACTION);
    put(method, 654, "get");
    assertThrows(LayoutValidationException.class, () -> decode(method));
    byte[] reserved = golden(ACTION_CATEGORY, MENU_ACTION);
    reserved[2067] = 'X';
    assertThrows(PermanentProtocolException.class, () -> decode(reserved));
    byte[] blankMethod = golden(ACTION_CATEGORY, MENU_ACTION);
    Arrays.fill(blankMethod, 653, 661, (byte) ' ');
    assertThrows(PermanentProtocolException.class, () -> decode(blankMethod));
  }

  @Test // PT-PRO-QA054-011
  void independentConcurrentCallersDoNotMixCategories() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> encode(legacy(Optional.empty())));
      var second = workers.submit(() -> encode(value(LogType.ACTION, Optional.of(MENU_ACTION))));
      assertArrayEquals(golden(REQUEST_CATEGORY, ""), first.get());
      assertArrayEquals(golden(ACTION_CATEGORY, MENU_ACTION), second.get());
    }
  }

  @Test // PT-PRO-QA054-012
  void recordFieldsAreCompleteImmutableAndRedacted() {
    var data = value(LogType.ACTION, Optional.of(MENU_ACTION));
    assertEquals(14, data.fields().names().size());
    assertEquals(data, WebLogEventData.from(data.fields()));
    assertEquals(AT, data.occurredAt());
    assertEquals(ID, data.httpRequestId());
    assertEquals(LogLevel.INFO, data.level());
    assertEquals(SAFE_MESSAGE, data.message());
    assertEquals(GET_METHOD, data.httpMethod());
    assertEquals("/", data.path());
    assertEquals(200, data.httpStatus().value());
    assertEquals(12, data.elapsedMs().value());
    assertEquals(ADDRESS, data.remoteAddress());
    assertEquals(Optional.of(USERNAME), data.username());
    assertEquals(Optional.of(UserRole.USER), data.role());
    assertEquals(Optional.of("{}"), data.details());
    assertEquals("WebLogEventData[REDACTED]", data.toString());
  }

  private static WebLogEventData legacy(Optional<String> action) {
    return new WebLogEventData(
        AT,
        LogLevel.INFO,
        action,
        SAFE_MESSAGE,
        ID,
        GET_METHOD,
        "/",
        new HttpStatusCode(200),
        new ElapsedMilliseconds(12),
        ADDRESS,
        Optional.of(USERNAME),
        Optional.of(UserRole.USER),
        Optional.of("{}"));
  }

  private static WebLogEventData value(LogType type, Optional<String> action) {
    return new WebLogEventData(
        AT,
        type,
        LogLevel.INFO,
        action,
        SAFE_MESSAGE,
        ID,
        GET_METHOD,
        "/",
        new HttpStatusCode(200),
        new ElapsedMilliseconds(12),
        ADDRESS,
        Optional.of(USERNAME),
        Optional.of(UserRole.USER),
        Optional.of("{}"));
  }

  private static byte[] encode(WebLogEventData value) {
    return PayloadCodec.standard()
        .encode(PayloadTypeCatalog.encode(new TypedPayloadValues(LAYOUT, value, List.of())), false)
        .copyData();
  }

  private static WebLogEventData decode(byte[] data) {
    return (WebLogEventData)
        PayloadTypeCatalog.decode(PayloadCodec.standard().decode(LAYOUT, data, List.of(), false))
            .data();
  }

  private static byte[] golden(String type, String action) {
    byte[] data = new byte[2080];
    Arrays.fill(data, (byte) ' ');
    // UI235 offsets/lengths are literals, independent of production catalog/codec.
    put(data, 1, "20261105090000000");
    put(data, 18, type);
    put(data, 34, "INFO");
    put(data, 42, action);
    put(data, 106, SAFE_MESSAGE);
    put(data, 618, ID.toString());
    put(data, 654, GET_METHOD);
    put(data, 662, "/");
    put(data, 918, "200");
    put(data, 921, "12"); // X9: numeric text followed by spaces, UI235.
    put(data, 930, ADDRESS);
    put(data, 975, USERNAME);
    put(data, 1039, "USER");
    put(data, 1044, "{}");
    return data;
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset - 1, bytes.length);
  }
}
