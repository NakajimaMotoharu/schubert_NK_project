package dev.codex.schubert.nk.protocol.header;

import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Type-safe 256-byte header model. Trace: NK-PRO-001, UI 232 §3/§5/§7, SS 322 §2/§7. */
public record CommonHeader(
    String protocolIdentifier,
    int headerVersion,
    LayoutId layoutId,
    int layoutVersion,
    MessageKind messageKind,
    InteractionKind interactionKind,
    UUID messageId,
    UUID correlationId,
    Instant sentAt,
    Optional<AuthenticationContext> authenticationContext,
    int headerLength,
    int dataLength,
    int recordLength,
    int recordCount,
    int totalLength,
    Optional<ResultCode> resultCode) {

  public static final String PROTOCOL_IDENTIFIER = "SCHBNK01";
  public static final int CURRENT_HEADER_VERSION = 1;
  public static final int CURRENT_LAYOUT_VERSION = 1;

  public CommonHeader {
    Objects.requireNonNull(protocolIdentifier, "protocolIdentifier");
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(messageKind, "messageKind");
    Objects.requireNonNull(interactionKind, "interactionKind");
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(sentAt, "sentAt");
    Objects.requireNonNull(authenticationContext, "authenticationContext");
    Objects.requireNonNull(resultCode, "resultCode");

    if (!PROTOCOL_IDENTIFIER.equals(protocolIdentifier)) {
      throw new LayoutValidationException("unsupported protocol identifier");
    }
    if (headerVersion != CURRENT_HEADER_VERSION || layoutVersion != CURRENT_LAYOUT_VERSION) {
      throw new LayoutValidationException("unsupported header or layout version");
    }
    if (headerLength != LayoutDefinition.HEADER_LENGTH) {
      throw new LayoutValidationException("header length must be 256 bytes");
    }
    if (dataLength < 0 || dataLength > 999_999
        || recordLength < 0 || recordLength > 999_999
        || recordCount < 0 || recordCount > 999_999) {
      throw new LayoutValidationException("declared length/count is outside its six-digit range");
    }
    if (recordLength == 0 && recordCount != 0) {
      throw new LayoutValidationException("record count requires a non-zero record length");
    }
    int calculatedTotal = calculateTotal(dataLength, recordLength, recordCount);
    if (totalLength != calculatedTotal) {
      throw new LayoutValidationException("total length does not match the checked length formula");
    }
    if (sentAt.getNano() % 1_000_000 != 0) {
      throw new LayoutValidationException("sent timestamp must have millisecond precision");
    }
    validateKinds(messageKind, interactionKind);
    validateCorrelation(messageKind, messageId, correlationId);
    validateResult(messageKind, recordCount, resultCode);
    validateAuthentication(layoutId, messageKind, authenticationContext);
  }

  public void validateAgainst(LayoutDefinition definition) {
    Objects.requireNonNull(definition, "definition");
    if (!layoutId.equals(definition.id())
        || messageKind != definition.messageKind()
        || interactionKind != definition.interactionKind()
        || dataLength != definition.dataLength()
        || recordLength != definition.recordLength()
        || recordCount > definition.maximumRecordCount()) {
      throw new LayoutValidationException("header does not match its layout definition");
    }
    definition.totalLengthFor(recordCount);
  }

  private static int calculateTotal(int dataLength, int recordLength, int recordCount) {
    final int total;
    try {
      total = Math.addExact(
          LayoutDefinition.HEADER_LENGTH,
          Math.addExact(dataLength, Math.multiplyExact(recordLength, recordCount)));
    } catch (ArithmeticException exception) {
      throw new LayoutValidationException("header length calculation overflow", exception);
    }
    if (total > LayoutDefinition.MAXIMUM_BODY_LENGTH) {
      throw new LayoutValidationException("message exceeds the one-million-byte body limit");
    }
    return total;
  }

  private static void validateKinds(MessageKind kind, InteractionKind interaction) {
    if ((kind == MessageKind.EVENT) != (interaction == InteractionKind.INTERNAL)) {
      throw new LayoutValidationException("event/internal message kinds must be paired");
    }
  }

  private static void validateCorrelation(MessageKind kind, UUID messageId, UUID correlationId) {
    if (kind == MessageKind.REQUEST && !messageId.equals(correlationId)) {
      throw new LayoutValidationException("root request correlation ID must equal its message ID");
    }
  }

  private static void validateResult(
      MessageKind kind, int recordCount, Optional<ResultCode> resultCode) {
    if ((kind == MessageKind.RESPONSE) != resultCode.isPresent()) {
      throw new LayoutValidationException("result code presence does not match message kind");
    }
    if (resultCode.isPresent()
        && !resultCode.orElseThrow().usesSuccessProfile()
        && recordCount != 0) {
      throw new LayoutValidationException("error response must have zero records");
    }
  }

  private static void validateAuthentication(
      LayoutId layoutId,
      MessageKind kind,
      Optional<AuthenticationContext> authenticationContext) {
    boolean mustBeAbsent =
        kind == MessageKind.EVENT
            || layoutId.value().equals("LGNREQ01")
            || layoutId.value().equals("LGNRSP01");
    if (mustBeAbsent == authenticationContext.isPresent()) {
      throw new LayoutValidationException("authentication context presence violates the layout profile");
    }
  }

  @Override
  public String toString() {
    return "CommonHeader[layoutId="
        + layoutId
        + ", messageKind="
        + messageKind
        + ", interactionKind="
        + interactionKind
        + ", messageId="
        + messageId
        + ", correlationId="
        + correlationId
        + ", totalLength="
        + totalLength
        + ", resultCode="
        + resultCode
        + ", authenticationContext=REDACTED]";
  }
}
