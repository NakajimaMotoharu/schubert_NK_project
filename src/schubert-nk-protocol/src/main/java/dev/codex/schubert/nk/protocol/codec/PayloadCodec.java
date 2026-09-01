package dev.codex.schubert.nk.protocol.codec;

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
import dev.codex.schubert.nk.protocol.layout.WireType;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Catalog-driven X/N/B payload codec. Trace: NK-PRO-002, UI 234-236, SS 322 §4-§6. */
public final class PayloadCodec {
  private static final PayloadCodec STANDARD = new PayloadCodec(LayoutFieldCatalog.standard());

  private final LayoutFieldCatalog catalog;

  private PayloadCodec(LayoutFieldCatalog catalog) {
    this.catalog = Objects.requireNonNull(catalog, "catalog");
  }

  public static PayloadCodec standard() {
    return STANDARD;
  }

  public FixedPayload encode(PayloadValues values, boolean errorProfile) {
    Objects.requireNonNull(values, "values");
    LayoutFields fields = catalog.require(values.layoutId());
    if (errorProfile && !values.records().isEmpty()) {
      throw new MessageEncodingException("error payload must not contain records");
    }
    if (values.records().size() > fields.layout().maximumRecordCount()) {
      throw new MessageEncodingException("payload record count exceeds its layout limit");
    }
    byte[] data = encodeArea(values.data(), fields.dataFields(), errorProfile);
    ArrayList<byte[]> records = new ArrayList<>(values.records().size());
    for (FieldValueSet record : values.records()) {
      records.add(encodeArea(record, fields.recordFields(), errorProfile));
    }
    return new FixedPayload(data, fields.layout().recordLength(), records);
  }

  public PayloadValues decode(
      LayoutId layoutId, byte[] data, List<byte[]> records, boolean errorProfile) {
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
    FieldValueSet decodedData = decodeArea(data, fields.dataFields(), errorProfile);
    ArrayList<FieldValueSet> decodedRecords = new ArrayList<>(records.size());
    for (byte[] record : records) {
      Objects.requireNonNull(record, "record");
      if (record.length != fields.layout().recordLength()) {
        throw new PermanentProtocolException("payload record length differs from its layout");
      }
      decodedRecords.add(decodeArea(record, fields.recordFields(), errorProfile));
    }
    return new PayloadValues(layoutId, decodedData, decodedRecords);
  }

  private static byte[] encodeArea(
      FieldValueSet values, List<FieldDefinition<?>> fields, boolean errorProfile) {
    validateNames(values, fields);
    int length = fields.isEmpty() ? 0 : fields.getLast().end();
    byte[] encoded = new byte[length];
    for (FieldDefinition<?> field : fields) {
      byte[] fieldBytes = encodeField(field, values.getOrUnset(field.name()), errorProfile);
      System.arraycopy(fieldBytes, 0, encoded, field.start() - 1, field.length());
    }
    return encoded;
  }

  private static FieldValueSet decodeArea(
      byte[] encoded, List<FieldDefinition<?>> fields, boolean errorProfile) {
    Map<String, FieldValue> values = new LinkedHashMap<>();
    for (FieldDefinition<?> field : fields) {
      byte[] fieldBytes =
          Arrays.copyOfRange(encoded, field.start() - 1, field.start() - 1 + field.length());
      if (field.presence() == Presence.FIXED) {
        validateFixed(field, fieldBytes);
      } else {
        values.put(field.name(), decodeField(field, fieldBytes, errorProfile));
      }
    }
    return new FieldValueSet(values);
  }

  private static void validateNames(
      FieldValueSet values, List<FieldDefinition<?>> fields) {
    for (String name : values.names()) {
      FieldDefinition<?> matching =
          fields.stream().filter(field -> field.name().equals(name)).findFirst().orElse(null);
      if (matching == null || matching.presence() == Presence.FIXED) {
        throw new MessageEncodingException("payload contains an unknown or fixed field value");
      }
    }
  }

  private static byte[] encodeField(
      FieldDefinition<?> field, FieldValue value, boolean errorProfile) {
    if (field.presence() == Presence.FIXED) {
      String fixedText = fixedText(field);
      return FieldCodec.encodeText(fixedText, field.length(), fixedText != null);
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
    return switch (field.wireType()) {
      case TEXT -> {
        if (!(value instanceof FieldValue.Text text)) {
          throw new MessageEncodingException("text payload field has the wrong Java type");
        }
        yield FieldCodec.encodeText(text.value(), field.length(), field.presence() == Presence.MANDATORY);
      }
      case NUMERIC -> {
        if (!(value instanceof FieldValue.Numeric numeric)) {
          throw new MessageEncodingException("numeric payload field has the wrong Java type");
        }
        yield FieldCodec.encodeNumeric(numeric.value(), field.length(), 0, maximumForDigits(field.length()));
      }
      case BOOLEAN -> {
        if (!(value instanceof FieldValue.Flag flag)) {
          throw new MessageEncodingException("boolean payload field has the wrong Java type");
        }
        yield FieldCodec.encodeBoolean(flag.value(), false);
      }
    };
  }

  private static FieldValue decodeField(
      FieldDefinition<?> field, byte[] encoded, boolean errorProfile) {
    if (errorProfile) {
      validateErrorFiller(field, encoded);
      return FieldValue.Unset.INSTANCE;
    }
    return switch (field.wireType()) {
      case TEXT ->
          FieldCodec.decodeText(encoded, field.presence() == Presence.MANDATORY)
              .<FieldValue>map(FieldValue.Text::new)
              .orElse(FieldValue.Unset.INSTANCE);
      case NUMERIC ->
          new FieldValue.Numeric(
              FieldCodec.decodeNumeric(encoded, 0, maximumForDigits(field.length())));
      case BOOLEAN ->
          new FieldValue.Flag(FieldCodec.decodeBoolean(encoded, false).orElseThrow());
    };
  }

  private static byte[] errorFiller(FieldDefinition<?> field) {
    return switch (field.wireType()) {
      case TEXT -> FieldCodec.encodeText(null, field.length(), false);
      case NUMERIC -> FieldCodec.encodeNumeric(0, field.length(), 0, maximumForDigits(field.length()));
      case BOOLEAN -> FieldCodec.encodeBoolean(null, true);
    };
  }

  private static void validateErrorFiller(FieldDefinition<?> field, byte[] encoded) {
    boolean valid =
        switch (field.wireType()) {
          case TEXT -> FieldCodec.decodeText(encoded, false).isEmpty();
          case NUMERIC ->
              FieldCodec.decodeNumericOrErrorFiller(
                      encoded, 0, maximumForDigits(field.length()), true)
                  .isEmpty();
          case BOOLEAN -> FieldCodec.decodeBoolean(encoded, true).isEmpty();
        };
    if (!valid) {
      throw new PermanentProtocolException("payload field does not use its error filler");
    }
  }

  private static void validateFixed(FieldDefinition<?> field, byte[] encoded) {
    String fixedText = fixedText(field);
    if (fixedText == null) {
      FieldCodec.requireSpaces(encoded);
      return;
    }
    String actual = FieldCodec.decodeText(encoded, true).orElseThrow();
    if (!actual.equals(fixedText)) {
      throw new PermanentProtocolException("fixed payload field has an unexpected value");
    }
  }

  private static String fixedText(FieldDefinition<?> field) {
    return field.name().equals("Log type") ? "REQUEST" : null;
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
