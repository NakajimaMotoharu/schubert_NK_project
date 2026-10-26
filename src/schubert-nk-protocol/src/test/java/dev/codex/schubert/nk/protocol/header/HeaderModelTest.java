package dev.codex.schubert.nk.protocol.header;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class HeaderModelTest {
  private static final String FALSE_TEXT = "false";
  private static final String LOG_REQUEST_LAYOUT = "LOGREQ01";
  private static final String GAME_RESPONSE_LAYOUT = "GAMRSP01";
  private static final UUID MESSAGE_ID = UUID.fromString("123e4567-e89b-12d3-a456-426614174000");
  private static final UUID OTHER_ID = UUID.fromString("223e4567-e89b-12d3-a456-426614174000");
  private static final Instant SENT_AT = Instant.parse("2026-09-02T03:34:56.789Z");
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void enumsMapOnlyApprovedWireValues() {
    assertEquals(MessageKind.REQUEST, MessageKind.fromWire("Q"));
    assertEquals(MessageKind.RESPONSE, MessageKind.fromWire("S"));
    assertEquals(MessageKind.EVENT, MessageKind.fromWire("E"));
    assertEquals('Q', MessageKind.REQUEST.wireValue());
    assertEquals(3, MessageKind.values().length);
    assertEquals(MessageKind.REQUEST, MessageKind.valueOf("REQUEST"));
    assertThrows(NullPointerException.class, () -> MessageKind.fromWire(null));
    assertThrows(IllegalArgumentException.class, () -> MessageKind.fromWire(""));
    assertThrows(IllegalArgumentException.class, () -> MessageKind.fromWire("QQ"));
    assertThrows(IllegalArgumentException.class, () -> MessageKind.fromWire("X"));

    assertEquals(InteractionKind.SYNCHRONOUS, InteractionKind.fromWire("S"));
    assertEquals(InteractionKind.ASYNC_ACCEPTANCE, InteractionKind.fromWire("A"));
    assertEquals(InteractionKind.INTERNAL, InteractionKind.fromWire("I"));
    assertEquals('A', InteractionKind.ASYNC_ACCEPTANCE.wireValue());
    assertEquals(3, InteractionKind.values().length);
    assertEquals(InteractionKind.INTERNAL, InteractionKind.valueOf("INTERNAL"));
    assertThrows(NullPointerException.class, () -> InteractionKind.fromWire(null));
    assertThrows(IllegalArgumentException.class, () -> InteractionKind.fromWire(""));
    assertThrows(IllegalArgumentException.class, () -> InteractionKind.fromWire("SS"));
    assertThrows(IllegalArgumentException.class, () -> InteractionKind.fromWire("X"));

    // BUG1279/YKT1045: decode uses a fixed switch, so roundtrip/name/count alone
    // cannot prove each encode wire value. These literals come from UI232 §3.
    String[][] kinds = {{"REQUEST", "Q"}, {"RESPONSE", "S"}, {"EVENT", "E"}};
    for (String[] row : kinds) {
      assertEquals(row[1].charAt(0), MessageKind.valueOf(row[0]).wireValue(), row[0]);
      assertEquals(row[0], MessageKind.fromWire(row[1]).name(), row[1]);
    }
    String[][] interactions = {{"SYNCHRONOUS", "S"}, {"ASYNC_ACCEPTANCE", "A"}, {"INTERNAL", "I"}};
    for (String[] row : interactions) {
      assertEquals(row[1].charAt(0), InteractionKind.valueOf(row[0]).wireValue(), row[0]);
      assertEquals(row[0], InteractionKind.fromWire(row[1]).name(), row[1]);
    }

    // BUG1244/YKT1010/PT-PRO-001-H01: UI232 section7 independent literal oracle.
    // Production values/wireValue are actuals only, never the expected allowlist.
    String[][] approved = {
      {"SUCCESS", "0000", "true"},
      {"VALIDATION_ERROR", "0100", FALSE_TEXT},
      {"AUTHENTICATION_FAILED", "0101", FALSE_TEXT},
      {"SESSION_INVALID", "0102", FALSE_TEXT},
      {"FORBIDDEN", "0103", FALSE_TEXT},
      {"NOT_FOUND", "0104", FALSE_TEXT},
      {"CONFLICT", "0105", FALSE_TEXT},
      {"LOCKED", "0106", FALSE_TEXT},
      {"NOT_CANCELLABLE", "0107", FALSE_TEXT},
      {"IDEMPOTENT_SUCCESS", "0200", "true"},
      {"TEMPORARY_FAILURE", "9000", FALSE_TEXT},
      {"RESOURCE_LIMIT", "9001", FALSE_TEXT}
    };
    assertEquals(12, ResultCode.values().length);
    for (String[] row : approved) {
      ResultCode actual = ResultCode.valueOf(row[0]);
      assertEquals(row[1], actual.wireValue(), row[0]);
      assertEquals(Boolean.parseBoolean(row[2]), actual.usesSuccessProfile(), row[0]);
      assertEquals(row[0], ResultCode.fromWire(row[1]).name(), row[1]);
    }
    for (String unknown : new String[] {"0199", "9900", "9999"})
      assertThrows(IllegalArgumentException.class, () -> ResultCode.fromWire(unknown));
    assertTrue(ResultCode.SUCCESS.usesSuccessProfile());
    assertTrue(ResultCode.IDEMPOTENT_SUCCESS.usesSuccessProfile());
    assertFalse(ResultCode.VALIDATION_ERROR.usesSuccessProfile());
    assertThrows(NullPointerException.class, () -> ResultCode.fromWire(null));
    assertThrows(IllegalArgumentException.class, () -> ResultCode.fromWire("9999"));
  }

  @Test
  void authenticationContextValidatesAndRedacts() {
    AuthenticationContext same = AuthenticationContext.of("a".repeat(64));
    AuthenticationContext different = AuthenticationContext.of("b".repeat(64));
    assertEquals(CONTEXT, same);
    assertEquals(CONTEXT.hashCode(), same.hashCode());
    assertNotEquals(CONTEXT, different);
    assertNotEquals(CONTEXT, "not-context");
    assertEquals("a".repeat(64), CONTEXT.wireValue());
    assertEquals("AuthenticationContext[REDACTED]", CONTEXT.toString());
    assertThrows(NullPointerException.class, () -> AuthenticationContext.of(null));
    assertThrows(IllegalArgumentException.class, () -> AuthenticationContext.of("a".repeat(63)));
    assertThrows(IllegalArgumentException.class, () -> AuthenticationContext.of("A".repeat(64)));
  }

  @Test
  void validHeadersCoverRequestResponseErrorAndEventProfiles() {
    CommonHeader loginRequest =
        header(
            "LGNREQ01",
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            384,
            0,
            0,
            Optional.empty(),
            Optional.empty());
    CommonHeader loginResponse =
        header(
            "LGNRSP01",
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            432,
            0,
            0,
            Optional.empty(),
            Optional.of(ResultCode.SUCCESS));
    CommonHeader ordinaryRequest =
        header(
            LOG_REQUEST_LAYOUT,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            0,
            0,
            0,
            Optional.of(CONTEXT),
            Optional.empty());
    CommonHeader ordinaryResponse =
        header(
            GAME_RESPONSE_LAYOUT,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            9,
            272,
            1,
            Optional.of(CONTEXT),
            Optional.of(ResultCode.IDEMPOTENT_SUCCESS));
    CommonHeader errorResponse =
        header(
            GAME_RESPONSE_LAYOUT,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            9,
            272,
            0,
            Optional.of(CONTEXT),
            Optional.of(ResultCode.NOT_FOUND));
    CommonHeader event =
        header(
            "WLGEVT01",
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            2_080,
            0,
            0,
            Optional.empty(),
            Optional.empty());

    loginRequest.validateAgainst(LayoutRegistry.standard().require("LGNREQ01", 1));
    loginResponse.validateAgainst(LayoutRegistry.standard().require("LGNRSP01", 1));
    ordinaryRequest.validateAgainst(LayoutRegistry.standard().require(LOG_REQUEST_LAYOUT, 1));
    ordinaryResponse.validateAgainst(LayoutRegistry.standard().require(GAME_RESPONSE_LAYOUT, 1));
    errorResponse.validateAgainst(LayoutRegistry.standard().require(GAME_RESPONSE_LAYOUT, 1));
    event.validateAgainst(LayoutRegistry.standard().require("WLGEVT01", 1));
    assertEquals(537, ordinaryResponse.totalLength());
    assertTrue(ordinaryRequest.toString().contains("authenticationContext=REDACTED"));
    assertFalse(ordinaryRequest.toString().contains("a".repeat(64)));
  }

  @Test
  void headerConstructorRejectsEveryStructuralViolation() {
    assertInvalid(base().protocol("OTHER001"));
    assertInvalid(base().headerVersion(2));
    assertInvalid(base().layoutVersion(2));
    assertInvalid(base().headerLength(255));
    assertInvalid(base().dataLength(-1));
    assertInvalid(base().dataLength(1_000_000));
    assertInvalid(base().recordLength(-1));
    assertInvalid(base().recordLength(1_000_000));
    assertInvalid(base().recordCount(-1));
    assertInvalid(base().recordCount(1_000_000));
    assertInvalid(base().recordLength(0).recordCount(1));
    assertInvalid(base().totalLength(999));
    assertInvalid(base().sentAt(Instant.parse("2026-09-02T03:34:56.789001Z")));
    assertInvalid(
        base()
            .kind(MessageKind.EVENT)
            .interaction(InteractionKind.SYNCHRONOUS)
            .context(Optional.empty()));
    assertInvalid(base().kind(MessageKind.REQUEST).interaction(InteractionKind.INTERNAL));
    assertInvalid(base().correlationId(OTHER_ID));
    assertInvalid(base().kind(MessageKind.RESPONSE).result(Optional.empty()));
    assertInvalid(base().result(Optional.of(ResultCode.SUCCESS)));
    assertInvalid(
        base()
            .kind(MessageKind.RESPONSE)
            .correlationId(OTHER_ID)
            .recordLength(1)
            .recordCount(1)
            .dataLength(0)
            .totalLength(257)
            .result(Optional.of(ResultCode.NOT_FOUND)));
    assertInvalid(
        base().layoutId("LGNREQ01").dataLength(384).totalLength(640).context(Optional.of(CONTEXT)));
    assertInvalid(base().context(Optional.empty()));
    assertInvalid(
        base()
            .kind(MessageKind.EVENT)
            .interaction(InteractionKind.INTERNAL)
            .layoutId("WLGEVT01")
            .dataLength(2_080)
            .totalLength(2_336)
            .context(Optional.of(CONTEXT)));
    assertInvalid(base().dataLength(999_999).totalLength(1_000_255));
    assertInvalid(base().dataLength(0).recordLength(999_999).recordCount(999_999).totalLength(256));
  }

  @Test
  void headerValidateAgainstRejectsEachMetadataMismatch() {
    CommonHeader header =
        header(
            LOG_REQUEST_LAYOUT,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            0,
            0,
            0,
            Optional.of(CONTEXT),
            Optional.empty());
    assertThrows(NullPointerException.class, () -> header.validateAgainst(null));
    assertMismatch(
        header,
        new LayoutDefinition(
            new LayoutId("GAMREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            0,
            0,
            0));
    assertMismatch(
        header,
        new LayoutDefinition(
            new LayoutId(LOG_REQUEST_LAYOUT),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            0,
            0,
            0));
    assertMismatch(
        header,
        new LayoutDefinition(
            new LayoutId(LOG_REQUEST_LAYOUT),
            1,
            MessageKind.REQUEST,
            InteractionKind.ASYNC_ACCEPTANCE,
            0,
            0,
            0));
    assertMismatch(
        header,
        new LayoutDefinition(
            new LayoutId(LOG_REQUEST_LAYOUT),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            1,
            0,
            0));
    assertMismatch(
        header,
        new LayoutDefinition(
            new LayoutId(LOG_REQUEST_LAYOUT),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            0,
            1,
            1));
    CommonHeader response =
        header(
            GAME_RESPONSE_LAYOUT,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            9,
            272,
            2,
            Optional.of(CONTEXT),
            Optional.of(ResultCode.SUCCESS));
    assertMismatch(
        response,
        new LayoutDefinition(
            new LayoutId(GAME_RESPONSE_LAYOUT),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            9,
            272,
            1));
  }

  private static void assertMismatch(CommonHeader header, LayoutDefinition definition) {
    assertThrows(LayoutValidationException.class, () -> header.validateAgainst(definition));
  }

  /** PT-PRO-HDR3266-001: immediate Java preconditions, not a wire success/error response. */
  @Test
  void headerReferencesRejectNullAtTheNamedInvariantBoundary() {
    String[] fields = {
      "protocolIdentifier",
      "layoutId",
      "messageKind",
      "interactionKind",
      "messageId",
      "correlationId",
      "sentAt",
      "authenticationContext",
      "resultCode"
    };
    for (int position = 0; position < fields.length; position++) {
      final int missing = position;
      var failure =
          assertThrows(NullPointerException.class, () -> headerWithMissingReference(missing));
      assertEquals(fields[position], failure.getMessage());
    }
    CommonHeader valid = headerWithMissingReference(-1);
    assertEquals(LOG_REQUEST_LAYOUT, valid.layoutId().value());
    assertEquals(256, valid.totalLength());
    assertEquals(MESSAGE_ID, valid.correlationId());
  }

  /** PT-PRO-HDR3266-002: UI232 constructor limits, independently of a layout's narrower cap. */
  @Test
  void headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow() {
    CommonHeader dataBoundary = base().dataLength(999_744).totalLength(1_000_000).build();
    assertEquals(999_744, dataBoundary.dataLength());
    assertEquals(1_000_000, dataBoundary.totalLength());
    CommonHeader recordBoundary =
        base().recordLength(1).recordCount(999_744).totalLength(1_000_000).build();
    assertEquals(999_744, recordBoundary.recordCount());
    assertEquals(1_000_000, recordBoundary.totalLength());
    assertInvalid(base().dataLength(999_745).totalLength(1_000_001));
    assertInvalid(base().recordLength(1).recordCount(999_745).totalLength(1_000_001));
    LayoutValidationException overflow =
        assertThrows(
            LayoutValidationException.class,
            () -> base().recordLength(999_999).recordCount(999_999).totalLength(256).build());
    assertTrue(overflow.getCause() instanceof ArithmeticException);
    assertEquals("header length calculation overflow", overflow.getMessage());
  }

  private static CommonHeader headerWithMissingReference(int missing) {
    return new CommonHeader(
        missing == 0 ? null : "SCHBNK01",
        1,
        missing == 1 ? null : new LayoutId(LOG_REQUEST_LAYOUT),
        1,
        missing == 2 ? null : MessageKind.REQUEST,
        missing == 3 ? null : InteractionKind.SYNCHRONOUS,
        missing == 4 ? null : MESSAGE_ID,
        missing == 5 ? null : MESSAGE_ID,
        missing == 6 ? null : SENT_AT,
        missing == 7 ? null : Optional.of(CONTEXT),
        256,
        0,
        0,
        0,
        256,
        missing == 8 ? null : Optional.empty());
  }

  private static void assertInvalid(HeaderBuilder builder) {
    assertThrows(LayoutValidationException.class, builder::build);
  }

  private static HeaderBuilder base() {
    return new HeaderBuilder();
  }

  private static CommonHeader header(
      String layoutId,
      MessageKind kind,
      InteractionKind interaction,
      int dataLength,
      int recordLength,
      int recordCount,
      Optional<AuthenticationContext> context,
      Optional<ResultCode> result) {
    UUID correlation = kind == MessageKind.REQUEST ? MESSAGE_ID : OTHER_ID;
    return new CommonHeader(
        CommonHeader.PROTOCOL_IDENTIFIER,
        1,
        new LayoutId(layoutId),
        1,
        kind,
        interaction,
        MESSAGE_ID,
        correlation,
        SENT_AT,
        context,
        256,
        dataLength,
        recordLength,
        recordCount,
        256 + dataLength + recordLength * recordCount,
        result);
  }

  private static final class HeaderBuilder {
    private String protocolValue = CommonHeader.PROTOCOL_IDENTIFIER;
    private int headerVersionValue = 1;
    private String layoutIdValue = LOG_REQUEST_LAYOUT;
    private int layoutVersionValue = 1;
    private MessageKind kindValue = MessageKind.REQUEST;
    private InteractionKind interactionValue = InteractionKind.SYNCHRONOUS;
    private UUID correlationIdValue = MESSAGE_ID;
    private Instant sentAtValue = SENT_AT;
    private Optional<AuthenticationContext> contextValue = Optional.of(CONTEXT);
    private int headerLengthValue = 256;
    private int dataLengthValue;
    private int recordLengthValue;
    private int recordCountValue;
    private int totalLengthValue = 256;
    private Optional<ResultCode> resultValue = Optional.empty();

    HeaderBuilder protocol(String value) {
      protocolValue = value;
      return this;
    }

    HeaderBuilder headerVersion(int value) {
      headerVersionValue = value;
      return this;
    }

    HeaderBuilder layoutId(String value) {
      layoutIdValue = value;
      return this;
    }

    HeaderBuilder layoutVersion(int value) {
      layoutVersionValue = value;
      return this;
    }

    HeaderBuilder kind(MessageKind value) {
      kindValue = value;
      return this;
    }

    HeaderBuilder interaction(InteractionKind value) {
      interactionValue = value;
      return this;
    }

    HeaderBuilder correlationId(UUID value) {
      correlationIdValue = value;
      return this;
    }

    HeaderBuilder sentAt(Instant value) {
      sentAtValue = value;
      return this;
    }

    HeaderBuilder context(Optional<AuthenticationContext> value) {
      contextValue = value;
      return this;
    }

    HeaderBuilder headerLength(int value) {
      headerLengthValue = value;
      return this;
    }

    HeaderBuilder dataLength(int value) {
      dataLengthValue = value;
      return this;
    }

    HeaderBuilder recordLength(int value) {
      recordLengthValue = value;
      return this;
    }

    HeaderBuilder recordCount(int value) {
      recordCountValue = value;
      return this;
    }

    HeaderBuilder totalLength(int value) {
      totalLengthValue = value;
      return this;
    }

    HeaderBuilder result(Optional<ResultCode> value) {
      resultValue = value;
      return this;
    }

    CommonHeader build() {
      return new CommonHeader(
          protocolValue,
          headerVersionValue,
          new LayoutId(layoutIdValue),
          layoutVersionValue,
          kindValue,
          interactionValue,
          MESSAGE_ID,
          correlationIdValue,
          sentAtValue,
          contextValue,
          headerLengthValue,
          dataLengthValue,
          recordLengthValue,
          recordCountValue,
          totalLengthValue,
          resultValue);
    }
  }
}
