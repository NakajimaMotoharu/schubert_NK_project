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

    for (ResultCode code : ResultCode.values()) {
      assertEquals(code, ResultCode.fromWire(code.wireValue()));
      assertEquals(code, ResultCode.valueOf(code.name()));
    }
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
    CommonHeader loginRequest = header("LGNREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 384, 0, 0, Optional.empty(), Optional.empty());
    CommonHeader loginResponse = header("LGNRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 432, 0, 0, Optional.empty(), Optional.of(ResultCode.SUCCESS));
    CommonHeader ordinaryRequest = header("LOGREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, Optional.of(CONTEXT), Optional.empty());
    CommonHeader ordinaryResponse = header("GAMRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 272, 1, Optional.of(CONTEXT), Optional.of(ResultCode.IDEMPOTENT_SUCCESS));
    CommonHeader errorResponse = header("GAMRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 272, 0, Optional.of(CONTEXT), Optional.of(ResultCode.NOT_FOUND));
    CommonHeader event = header("WLGEVT01", MessageKind.EVENT, InteractionKind.INTERNAL, 2_080, 0, 0, Optional.empty(), Optional.empty());

    loginRequest.validateAgainst(LayoutRegistry.standard().require("LGNREQ01", 1));
    loginResponse.validateAgainst(LayoutRegistry.standard().require("LGNRSP01", 1));
    ordinaryRequest.validateAgainst(LayoutRegistry.standard().require("LOGREQ01", 1));
    ordinaryResponse.validateAgainst(LayoutRegistry.standard().require("GAMRSP01", 1));
    errorResponse.validateAgainst(LayoutRegistry.standard().require("GAMRSP01", 1));
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
    assertInvalid(base().kind(MessageKind.EVENT).interaction(InteractionKind.SYNCHRONOUS).context(Optional.empty()));
    assertInvalid(base().kind(MessageKind.REQUEST).interaction(InteractionKind.INTERNAL));
    assertInvalid(base().correlationId(OTHER_ID));
    assertInvalid(base().kind(MessageKind.RESPONSE).result(Optional.empty()));
    assertInvalid(base().result(Optional.of(ResultCode.SUCCESS)));
    assertInvalid(base().kind(MessageKind.RESPONSE).correlationId(OTHER_ID).recordLength(1).recordCount(1).dataLength(0).totalLength(257).result(Optional.of(ResultCode.NOT_FOUND)));
    assertInvalid(base().layoutId("LGNREQ01").dataLength(384).totalLength(640).context(Optional.of(CONTEXT)));
    assertInvalid(base().context(Optional.empty()));
    assertInvalid(base().kind(MessageKind.EVENT).interaction(InteractionKind.INTERNAL).layoutId("WLGEVT01").dataLength(2_080).totalLength(2_336).context(Optional.of(CONTEXT)));
    assertInvalid(base().dataLength(999_999).totalLength(1_000_255));
    assertInvalid(base().dataLength(0).recordLength(999_999).recordCount(999_999).totalLength(256));
  }

  @Test
  void headerValidateAgainstRejectsEachMetadataMismatch() {
    CommonHeader header = header("LOGREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, Optional.of(CONTEXT), Optional.empty());
    assertThrows(NullPointerException.class, () -> header.validateAgainst(null));
    assertMismatch(header, new LayoutDefinition(new LayoutId("GAMREQ01"), 1, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0));
    assertMismatch(header, new LayoutDefinition(new LayoutId("LOGREQ01"), 1, MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 0, 0, 0));
    assertMismatch(header, new LayoutDefinition(new LayoutId("LOGREQ01"), 1, MessageKind.REQUEST, InteractionKind.ASYNC_ACCEPTANCE, 0, 0, 0));
    assertMismatch(header, new LayoutDefinition(new LayoutId("LOGREQ01"), 1, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 1, 0, 0));
    assertMismatch(header, new LayoutDefinition(new LayoutId("LOGREQ01"), 1, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 1, 1));
    CommonHeader response = header("GAMRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 272, 2, Optional.of(CONTEXT), Optional.of(ResultCode.SUCCESS));
    assertMismatch(response, new LayoutDefinition(new LayoutId("GAMRSP01"), 1, MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 272, 1));
  }

  private static void assertMismatch(CommonHeader header, LayoutDefinition definition) {
    assertThrows(LayoutValidationException.class, () -> header.validateAgainst(definition));
  }

  private static void assertInvalid(HeaderBuilder builder) {
    assertThrows(RuntimeException.class, builder::build);
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
    private String protocol = CommonHeader.PROTOCOL_IDENTIFIER;
    private int headerVersion = 1;
    private String layoutId = "LOGREQ01";
    private int layoutVersion = 1;
    private MessageKind kind = MessageKind.REQUEST;
    private InteractionKind interaction = InteractionKind.SYNCHRONOUS;
    private UUID correlationId = MESSAGE_ID;
    private Instant sentAt = SENT_AT;
    private Optional<AuthenticationContext> context = Optional.of(CONTEXT);
    private int headerLength = 256;
    private int dataLength;
    private int recordLength;
    private int recordCount;
    private int totalLength = 256;
    private Optional<ResultCode> result = Optional.empty();

    HeaderBuilder protocol(String value) { protocol = value; return this; }
    HeaderBuilder headerVersion(int value) { headerVersion = value; return this; }
    HeaderBuilder layoutId(String value) { layoutId = value; return this; }
    HeaderBuilder layoutVersion(int value) { layoutVersion = value; return this; }
    HeaderBuilder kind(MessageKind value) { kind = value; return this; }
    HeaderBuilder interaction(InteractionKind value) { interaction = value; return this; }
    HeaderBuilder correlationId(UUID value) { correlationId = value; return this; }
    HeaderBuilder sentAt(Instant value) { sentAt = value; return this; }
    HeaderBuilder context(Optional<AuthenticationContext> value) { context = value; return this; }
    HeaderBuilder headerLength(int value) { headerLength = value; return this; }
    HeaderBuilder dataLength(int value) { dataLength = value; return this; }
    HeaderBuilder recordLength(int value) { recordLength = value; return this; }
    HeaderBuilder recordCount(int value) { recordCount = value; return this; }
    HeaderBuilder totalLength(int value) { totalLength = value; return this; }
    HeaderBuilder result(Optional<ResultCode> value) { result = value; return this; }

    CommonHeader build() {
      return new CommonHeader(
          protocol,
          headerVersion,
          new LayoutId(layoutId),
          layoutVersion,
          kind,
          interaction,
          MESSAGE_ID,
          correlationId,
          sentAt,
          context,
          headerLength,
          dataLength,
          recordLength,
          recordCount,
          totalLength,
          result);
    }
  }
}
