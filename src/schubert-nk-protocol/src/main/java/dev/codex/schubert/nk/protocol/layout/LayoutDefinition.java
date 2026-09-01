package dev.codex.schubert.nk.protocol.layout;

import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.util.Objects;

/** Immutable UI 233 layout tuple. Trace: NK-PRO-001, UI 233, SS 322 §2/§12. */
public record LayoutDefinition(
    LayoutId id,
    int version,
    MessageKind messageKind,
    InteractionKind interactionKind,
    int dataLength,
    int recordLength,
    int maximumRecordCount,
    int maximumTotalLength) {

  public static final int HEADER_LENGTH = 256;
  public static final int MAXIMUM_BODY_LENGTH = 1_000_000;
  private static final int MAXIMUM_DECLARED_FIELD_LENGTH = 999_999;

  public LayoutDefinition(
      LayoutId id,
      int version,
      MessageKind messageKind,
      InteractionKind interactionKind,
      int dataLength,
      int recordLength,
      int maximumRecordCount) {
    this(
        id,
        version,
        messageKind,
        interactionKind,
        dataLength,
        recordLength,
        maximumRecordCount,
        calculateMaximumTotal(dataLength, recordLength, maximumRecordCount));
  }

  public LayoutDefinition {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(messageKind, "messageKind");
    Objects.requireNonNull(interactionKind, "interactionKind");
    if (version != 1) {
      throw new LayoutValidationException("only layout version 001 is supported");
    }
    validateDeclaredLength("dataLength", dataLength);
    validateDeclaredLength("recordLength", recordLength);
    validateDeclaredLength("maximumRecordCount", maximumRecordCount);
    if ((recordLength == 0) != (maximumRecordCount == 0)) {
      throw new LayoutValidationException("record length and maximum count must both be zero or non-zero");
    }
    int calculated = calculateMaximumTotal(dataLength, recordLength, maximumRecordCount);
    if (maximumTotalLength != calculated) {
      throw new LayoutValidationException("maximum total length does not match the checked length formula");
    }
    if (messageKind == MessageKind.EVENT
        && interactionKind != InteractionKind.INTERNAL) {
      throw new LayoutValidationException("event layout must use internal interaction");
    }
    if (messageKind != MessageKind.EVENT
        && interactionKind == InteractionKind.INTERNAL) {
      throw new LayoutValidationException("request/response layout cannot use internal interaction");
    }
  }

  public int totalLengthFor(int recordCount) {
    if (recordCount < 0 || recordCount > maximumRecordCount) {
      throw new LayoutValidationException("record count is outside the layout limit");
    }
    return calculateMaximumTotal(dataLength, recordLength, recordCount);
  }

  private static void validateDeclaredLength(String name, int value) {
    if (value < 0 || value > MAXIMUM_DECLARED_FIELD_LENGTH) {
      throw new LayoutValidationException(name + " is outside its six-digit range");
    }
  }

  private static int calculateMaximumTotal(int dataLength, int recordLength, int recordCount) {
    validateDeclaredLength("dataLength", dataLength);
    validateDeclaredLength("recordLength", recordLength);
    validateDeclaredLength("recordCount", recordCount);
    final int total;
    try {
      total = Math.addExact(HEADER_LENGTH, Math.addExact(dataLength, Math.multiplyExact(recordLength, recordCount)));
    } catch (ArithmeticException exception) {
      throw new LayoutValidationException("layout length calculation overflow", exception);
    }
    if (total > MAXIMUM_BODY_LENGTH) {
      throw new LayoutValidationException("layout exceeds the one-million-byte body limit");
    }
    return total;
  }
}
