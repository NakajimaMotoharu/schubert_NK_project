package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldDefinition;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalog;
import dev.codex.schubert.nk.protocol.layout.LayoutFields;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.Presence;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Catalog-driven X/N/B payload codec. Trace: NK-PRO-002, UI 234-236, SS 322 §4-§6. */
public final class PayloadCodec {
  private static final PayloadCodec RETAINED_STANDARD =
      new PayloadCodec(LayoutFieldCatalog.standard());

  private final LayoutFieldCatalog catalog;

  private PayloadCodec(LayoutFieldCatalog catalog) {
    this.catalog = Objects.requireNonNull(catalog, "catalog");
  }

  public static PayloadCodec standard() {
    return RETAINED_STANDARD;
  }

  public FixedPayload encode(PayloadValues values, boolean errorProfile) {
    return encode(values, errorProfile, Optional.empty());
  }

  /**
   * Encode one normal record without inventing a DATA/header or applying inline count limits.
   * Caller validates whole-list sequence semantics separately. SS322/333; PT-SCN-008-W03.
   */
  public byte[] encodeRecord(LayoutId layoutId, FieldValueSet record) {
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(record, "record");
    LayoutFields fields = catalog.require(layoutId);
    if (fields.layout().recordLength() == 0) {
      throw new MessageEncodingException("layout has no record area");
    }
    return encodeArea(record, fields.recordFields(), false, layoutId, Optional.empty());
  }

  /**
   * Decode one normal record without fabricating DATA/header. Caller checks file integrity and
   * whole-list sequence separately. SS322/333; PT-SCN-008-RD02.
   */
  public FieldValueSet decodeRecord(LayoutId layoutId, byte[] record) {
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(record, "record");
    LayoutFields fields = catalog.require(layoutId);
    if (fields.layout().recordLength() == 0) {
      throw new PermanentProtocolException("layout has no record area");
    }
    if (record.length != fields.layout().recordLength()) {
      throw new PermanentProtocolException("payload record length differs from its layout");
    }
    return decodeArea(record, fields.recordFields(), false, layoutId, Optional.empty());
  }

  /** Encodes a response using the result-code profile, including layout-specific error fields. */
  public FixedPayload encode(PayloadValues values, ResultCode resultCode) {
    Objects.requireNonNull(resultCode, "resultCode");
    return encode(values, !resultCode.usesSuccessProfile(), Optional.of(resultCode));
  }

  private FixedPayload encode(
      PayloadValues values, boolean errorProfile, Optional<ResultCode> resultCode) {
    Objects.requireNonNull(values, "values");
    LayoutFields fields = catalog.require(values.layoutId());
    if (errorProfile && !values.records().isEmpty()) {
      throw new MessageEncodingException("error payload must not contain records");
    }
    if (values.records().size() > fields.layout().maximumRecordCount()) {
      throw new MessageEncodingException("payload record count exceeds its layout limit");
    }
    validateErrorOverrideForEncode(values.layoutId(), values.data(), errorProfile, resultCode);
    byte[] data =
        encodeArea(values.data(), fields.dataFields(), errorProfile, values.layoutId(), resultCode);
    ArrayList<byte[]> records = new ArrayList<>(values.records().size());
    for (FieldValueSet record : values.records()) {
      records.add(
          encodeArea(record, fields.recordFields(), errorProfile, values.layoutId(), resultCode));
    }
    return new FixedPayload(data, fields.layout().recordLength(), records);
  }

  public PayloadValues decode(
      LayoutId layoutId, byte[] data, List<byte[]> records, boolean errorProfile) {
    return decode(layoutId, data, records, errorProfile, Optional.empty());
  }

  /** Decodes a response using the result-code profile, including layout-specific error fields. */
  public PayloadValues decode(
      LayoutId layoutId, byte[] data, List<byte[]> records, ResultCode resultCode) {
    Objects.requireNonNull(resultCode, "resultCode");
    return decode(
        layoutId, data, records, !resultCode.usesSuccessProfile(), Optional.of(resultCode));
  }

  private PayloadValues decode(
      LayoutId layoutId,
      byte[] data,
      List<byte[]> records,
      boolean errorProfile,
      Optional<ResultCode> resultCode) {
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(data, "data");
    Objects.requireNonNull(records, "records");
    LayoutFields fields = catalog.require(layoutId);
    if (data.length != fields.layout().dataLength()) {
      throw new PermanentProtocolException("payload data length differs from its layout");
    }
    if (errorProfile && !records.isEmpty()) {
      throw new PermanentProtocolException("error payload contains records");
    }
    if (records.size() > fields.layout().maximumRecordCount()) {
      throw new PermanentProtocolException("payload record count exceeds its layout limit");
    }
    FieldValueSet decodedData =
        decodeArea(data, fields.dataFields(), errorProfile, layoutId, resultCode);
    ArrayList<FieldValueSet> decodedRecords = new ArrayList<>(records.size());
    for (byte[] record : records) {
      Objects.requireNonNull(record, "record");
      if (record.length != fields.layout().recordLength()) {
        throw new PermanentProtocolException("payload record length differs from its layout");
      }
      decodedRecords.add(
          decodeArea(record, fields.recordFields(), errorProfile, layoutId, resultCode));
    }
    validateErrorOverride(layoutId, decodedData, errorProfile, resultCode);
    return new PayloadValues(layoutId, decodedData, decodedRecords);
  }

  private static byte[] encodeArea(
      FieldValueSet values,
      List<FieldDefinition<?>> fields,
      boolean errorProfile,
      LayoutId layoutId,
      Optional<ResultCode> resultCode) {
    validateNames(values, fields);
    int length = fields.isEmpty() ? 0 : fields.getLast().end();
    byte[] encoded = new byte[length];
    for (FieldDefinition<?> field : fields) {
      boolean useErrorFiller = errorProfile && !isErrorOverride(layoutId, resultCode, field.name());
      byte[] fieldBytes = encodeField(field, values.getOrUnset(field.name()), useErrorFiller);
      System.arraycopy(fieldBytes, 0, encoded, field.start() - 1, field.length());
    }
    return encoded;
  }

  private static FieldValueSet decodeArea(
      byte[] encoded,
      List<FieldDefinition<?>> fields,
      boolean errorProfile,
      LayoutId layoutId,
      Optional<ResultCode> resultCode) {
    Map<String, FieldValue> values = new LinkedHashMap<>();
    for (FieldDefinition<?> field : fields) {
      byte[] fieldBytes =
          Arrays.copyOfRange(encoded, field.start() - 1, field.start() - 1 + field.length());
      if (field.presence() == Presence.FIXED) {
        FieldCodec.requireSpaces(fieldBytes);
      } else {
        boolean useErrorFiller =
            errorProfile && !isErrorOverride(layoutId, resultCode, field.name());
        values.put(field.name(), decodeField(field, fieldBytes, useErrorFiller));
      }
    }
    return new FieldValueSet(values);
  }

  private static void validateNames(FieldValueSet values, List<FieldDefinition<?>> fields) {
    for (String name : values.names()) {
      Optional<FieldDefinition<?>> matching =
          fields.stream().filter(field -> field.name().equals(name)).findFirst();
      if (matching.isEmpty() || matching.orElseThrow().presence() == Presence.FIXED) {
        throw new MessageEncodingException("payload contains an unknown or fixed field value");
      }
    }
  }

  private static byte[] encodeField(
      FieldDefinition<?> field, FieldValue value, boolean errorProfile) {
    if (field.presence() == Presence.FIXED) {
      return FieldCodec.encodeText(null, field.length(), false);
    }
    if (errorProfile) {
      return errorFiller(field);
    }
    if (value == FieldValue.Unset.INSTANCE) {
      if (field.presence() == Presence.MANDATORY) {
        throw new MessageEncodingException("mandatory payload field is unset");
      }
      return FieldCodec.encodeText(null, field.length(), false);
    }
    {
      final WireType dispatchValue0 = java.util.Objects.requireNonNull(field.wireType());
      if (dispatchValue0 == WireType.TEXT) {

        if (!(value instanceof FieldValue.Text text)) {
          throw new MessageEncodingException("text payload field has the wrong Java type");
        }
        return FieldCodec.encodeText(
            text.value(), field.length(), field.presence() == Presence.MANDATORY);

      } else if (dispatchValue0 == WireType.NUMERIC) {

        if (!(value instanceof FieldValue.Numeric numeric)) {
          throw new MessageEncodingException("numeric payload field has the wrong Java type");
        }
        return FieldCodec.encodeNumeric(
            numeric.value(), field.length(), 0, maximumForDigits(field.length()));

      } else {

        if (!(value instanceof FieldValue.Flag flag)) {
          throw new MessageEncodingException("boolean payload field has the wrong Java type");
        }
        return FieldCodec.encodeBoolean(flag.value(), false);
      }
    }
  }

  private static FieldValue decodeField(
      FieldDefinition<?> field, byte[] encoded, boolean errorProfile) {
    if (errorProfile) {
      validateErrorFiller(field, encoded);
      return FieldValue.Unset.INSTANCE;
    }
    {
      final WireType dispatchValue1 = java.util.Objects.requireNonNull(field.wireType());
      if (dispatchValue1 == WireType.TEXT) {
        return FieldCodec.decodeText(encoded, field.presence() == Presence.MANDATORY)
            .<FieldValue>map(FieldValue.Text::new)
            .orElse(FieldValue.Unset.INSTANCE);
      } else if (dispatchValue1 == WireType.NUMERIC) {
        return new FieldValue.Numeric(
            FieldCodec.decodeNumeric(encoded, 0, maximumForDigits(field.length())));
      } else {
        return new FieldValue.Flag(FieldCodec.decodeBoolean(encoded, false).orElseThrow());
      }
    }
  }

  private static byte[] errorFiller(FieldDefinition<?> field) {
    {
      final WireType dispatchValue2 = java.util.Objects.requireNonNull(field.wireType());
      if (dispatchValue2 == WireType.TEXT) {
        return FieldCodec.encodeText(null, field.length(), false);
      } else if (dispatchValue2 == WireType.NUMERIC) {
        return FieldCodec.encodeNumeric(0, field.length(), 0, maximumForDigits(field.length()));
      } else {
        return FieldCodec.encodeBoolean(null, true);
      }
    }
  }

  private static void validateErrorFiller(FieldDefinition<?> field, byte[] encoded) {
    boolean valid;
    {
      final WireType dispatchValue3 = java.util.Objects.requireNonNull(field.wireType());
      if (dispatchValue3 == WireType.TEXT) {
        valid = FieldCodec.decodeText(encoded, false).isEmpty();
      } else if (dispatchValue3 == WireType.NUMERIC) {
        valid =
            FieldCodec.decodeNumericOrErrorFiller(
                    encoded, 0, maximumForDigits(field.length()), true)
                .isEmpty();
      } else {
        valid = FieldCodec.decodeBoolean(encoded, true).isEmpty();
      }
    }
    if (!valid) {
      throw new PermanentProtocolException("payload field does not use its error filler");
    }
  }

  private static boolean isErrorOverride(
      LayoutId layoutId, Optional<ResultCode> resultCode, String fieldName) {
    // Both callers invoke this only inside an error-profile path; no second profile inference.
    if (layoutId.value().equals("LGNRSP01") && resultCode.isPresent()) {
      return fieldName.equals("利用者message")
          || (fieldName.equals("Retry after秒") && resultCode.orElseThrow() == ResultCode.LOCKED);
    }
    return resultCode.equals(Optional.of(ResultCode.NOT_CANCELLABLE))
        && layoutId.value().equals("NTCRSP01")
        && fieldName.equals("更新後状態");
  }

  private static void validateErrorOverride(
      LayoutId layoutId,
      FieldValueSet data,
      boolean errorProfile,
      Optional<ResultCode> resultCode) {
    if (errorProfile && layoutId.value().equals("LGNRSP01") && resultCode.isPresent()) {
      FieldValue retry = data.getOrUnset("Retry after秒");
      if (resultCode.orElseThrow() == ResultCode.LOCKED) {
        if (!(retry instanceof FieldValue.Numeric value)
            || value.value() < 0
            || value.value() > 900)
          throw new PermanentProtocolException("login lock retry is outside 0..900");
      } else if (retry != FieldValue.Unset.INSTANCE
          && (!(retry instanceof FieldValue.Numeric value) || value.value() != 0)) {
        throw new PermanentProtocolException("non-lock login error contains a retry delay");
      }
    }
    if (!errorProfile || !isErrorOverride(layoutId, resultCode, "更新後状態")) {
      return;
    }
    FieldValue value = data.getOrUnset("更新後状態");
    if (!(value instanceof FieldValue.Text text)
        || !(text.value().equals("PROCESSING")
            || text.value().equals("COMPLETED")
            || text.value().equals("ERROR"))) {
      throw new PermanentProtocolException(
          "notification cancellation conflict contains an invalid latest state");
    }
  }

  private static void validateErrorOverrideForEncode(
      LayoutId layoutId,
      FieldValueSet data,
      boolean errorProfile,
      Optional<ResultCode> resultCode) {
    try {
      validateErrorOverride(layoutId, data, errorProfile, resultCode);
    } catch (PermanentProtocolException failure) {
      throw new MessageEncodingException("response contains invalid individual error fields");
    }
  }

  static long maximumForDigits(int length) {
    if (length < 1 || length > 18) {
      throw new LayoutValidationException("numeric field length is outside signed-long digits");
    }
    long maximum = 0;
    for (int index = 0; index < length; index++) {
      maximum = maximum * 10 + 9;
    }
    return maximum;
  }
}
