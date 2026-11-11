package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.ProtocolId;
import dev.codex.schubert.nk.protocol.layout.semantic.WireEnum;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.ParameterizedType;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * BUG1288/YKT1054: independent UI/SS scalar values and explicit public API bindings. Public
 * method/constructor invocation only; never infer record/private field order. Metadata and expected
 * values are not obtained from a Production method/generator.
 */
final class IndependentNamedFieldOracle {
  private static final int JST_WIRE_DIGITS = 17;
  private static final int ACCEPTED_NUMERIC_BOUNDARY_VECTORS = 2;
  private static final int UUID_TEXT_LENGTH = 36;
  private static final String SEMANTIC = "dev.codex.schubert.nk.protocol.layout.semantic.";
  private static final Instant TIME = Instant.parse("2026-09-02T03:34:56Z");
  private static final DateTimeFormatter JST =
      DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS").withZone(ZoneId.of("Asia/Tokyo"));
  private static final Map<String, String> ENUM_MEMBERS =
      Map.ofEntries(
          Map.entry("ContentDisposition", "INLINE"),
          Map.entry("DeliveryMode", "INLINE"),
          Map.entry("PairRole", "MAIN"),
          Map.entry("VoiceCondition", "PRESENT"),
          Map.entry("UserRole", "ADMIN"),
          Map.entry("LogLevel", "WARN"),
          Map.entry("LogType", "SECURITY"),
          Map.entry("UserState", "LOCKED"),
          Map.entry("NotificationState", "PROCESSING"),
          Map.entry("AnswerState", "ANSWERED"),
          Map.entry("NotificationType", "COMPLETED"),
          Map.entry("EntryType", "DIALOGUE"),
          Map.entry("GameCode", "NUKITASHI_2"),
          Map.entry("MediaMimeType", "AUDIO_OGG"),
          Map.entry("NotificationErrorCode", "PROCESS_FAILED"),
          Map.entry("AnimationListCategory", "OVA"),
          Map.entry("AnimationCategory", "SUBTRACK"),
          Map.entry("VideoCategory", "OPENING"));
  private static final Map<String, String> ENUM_WIRE =
      Map.ofEntries(
          Map.entry("ContentDisposition", "I"),
          Map.entry("DeliveryMode", "I"),
          Map.entry("PairRole", "M"),
          Map.entry("VoiceCondition", "1"),
          Map.entry("UserRole", "ADMIN"),
          Map.entry("LogLevel", "WARN"),
          Map.entry("LogType", "SECURITY"),
          Map.entry("UserState", "LOCKED"),
          Map.entry("NotificationState", "PROCESSING"),
          Map.entry("AnswerState", "ANSWERED"),
          Map.entry("NotificationType", "COMPLETED"),
          Map.entry("EntryType", "dialogue"),
          Map.entry("GameCode", "NUKITASHI2"),
          Map.entry("MediaMimeType", "audio/ogg"),
          Map.entry("NotificationErrorCode", "PROCESS_FAILED"),
          Map.entry("AnimationListCategory", "OVA"),
          Map.entry("AnimationCategory", "SUBTRACK"),
          Map.entry("VideoCategory", "OPENING"));

  private IndependentNamedFieldOracle() {}

  static void verifyAll() throws Exception {
    Map<String, String> accessors = new LinkedHashMap<>();
    for (String[] row : fixture("named-accessors-independent.tsv")) {
      assertEquals(2, row.length);
      assertEquals(null, accessors.put(row[0], row[1]), row[0]);
    }
    Map<String, List<Field>> areas = new HashMap<>();
    for (String[] row : fixture("fields-ui234-236.tsv")) {
      assertEquals(8, row.length);
      if (!row[6].equals("F"))
        areas
            .computeIfAbsent(row[0] + ":" + row[1], ignored -> new ArrayList<>())
            .add(new Field(row[2], Integer.parseInt(row[4]), row[5], row[6]));
    }
    Map<String, List<Field>> reviewed = new HashMap<>();
    Set<String> usedNames = new HashSet<>();
    int components = 0;
    int optionals = 0;
    int emptyTypes = 0;
    for (String[] mapping : fixture("named-types-ss323.tsv")) {
      assertEquals(3, mapping.length);
      LayoutId id = new LayoutId(mapping[0]);
      for (int area = 1; area <= 2; area++) {
        if (mapping[area].equals("-")) continue;
        Class<?> type =
            area == 1
                ? PayloadTypeCatalog.dataType(id)
                : PayloadTypeCatalog.recordType(id).orElseThrow();
        assertEquals(mapping[area], type.getSimpleName(), mapping[0]);
        List<Field> fields =
            areas.getOrDefault(mapping[0] + (area == 1 ? ":DATA" : ":RECORD"), List.of());
        List<Field> prior = reviewed.putIfAbsent(mapping[area], fields);
        if (prior != null) {
          assertEquals(prior, fields, mapping[area] + " shared canonical shape");
          continue;
        }
        components += fields.size();
        if (fields.isEmpty()) emptyTypes++;
        optionals += verifyType(type, mapping[0], fields, accessors, usedNames);
      }
    }
    assertEquals(69, reviewed.size(), "SS323 complete named type inventory");
    assertEquals(296, components, "independent canonical nonfixed component inventory");
    assertEquals(79, optionals, "independent canonical X/C/O component inventory");
    assertEquals(4, emptyTypes, "explicit no-data request types");
    assertEquals(usedNames, accessors.keySet(), "no missing/extra independent public API binding");
  }

  private static int verifyType(
      Class<?> type,
      String layout,
      List<Field> fields,
      Map<String, String> accessors,
      Set<String> usedNames)
      throws Exception {
    LinkedHashMap<String, FieldValue> input = new LinkedHashMap<>();
    List<Class<?>> signature = new ArrayList<>();
    List<Object> arguments = new ArrayList<>();
    List<Method> getters = new ArrayList<>();
    int index = 0;
    int optionals = 0;
    for (Field field : fields) {
      usedNames.add(field.name());
      String name = accessors.get(field.name());
      assertNotNull(name, field.name());
      Method getter = type.getMethod(name);
      Class<?> scalar = scalarType(field, layout);
      Class<?> rawType = field.optional() ? Optional.class : scalar;
      assertEquals(rawType, getter.getReturnType(), type.getSimpleName() + ":" + name);
      if (field.optional()) {
        var generic = assertInstanceOf(ParameterizedType.class, getter.getGenericReturnType());
        assertEquals(scalar, generic.getActualTypeArguments()[0], field.name());
        optionals++;
      }
      index++;
      FieldValue wire = independentWire(field, scalar, index);
      input.put(field.name(), wire);
      Object argument = independentInput(scalar, wire, index);
      arguments.add(field.optional() ? Optional.of(argument) : argument);
      signature.add(rawType);
      getters.add(getter);
    }
    Method from = type.getMethod("from", FieldValueSet.class);
    Object decoded = from.invoke(null, new FieldValueSet(input));
    for (int n = 0; n < fields.size(); n++) {
      Field field = fields.get(n);
      Object actual = getters.get(n).invoke(decoded);
      if (field.optional()) actual = assertInstanceOf(Optional.class, actual).orElseThrow();
      assertScalar(
          input.get(field.name()), actual, n + 1, type.getSimpleName() + ":" + field.name());
    }
    // Constructor signature/order comes from independent canonical field rows,
    // not getRecordComponents(), getDeclaredFields(), or Production mapper code.
    var constructor = type.getConstructor(signature.toArray(Class<?>[]::new));
    Object constructed = constructor.newInstance(arguments.toArray());
    assertWireMap(input, fieldsOf(constructed));
    for (int n = 0; n < fields.size(); n++) {
      Field field = fields.get(n);
      if (!signature.get(n).isPrimitive()) {
        Object[] bad = arguments.toArray();
        bad[n] = null;
        var failure =
            assertThrows(InvocationTargetException.class, () -> constructor.newInstance(bad));
        var cause = assertInstanceOf(NullPointerException.class, failure.getCause());
        assertEquals(accessors.get(field.name()), cause.getMessage(), type.getSimpleName());
      }
      if (field.optional()) {
        Map<String, FieldValue> absent = new LinkedHashMap<>(input);
        absent.put(field.name(), FieldValue.Unset.INSTANCE);
        Object optionalDecoded = from.invoke(null, new FieldValueSet(absent));
        assertEquals(Optional.empty(), getters.get(n).invoke(optionalDecoded), field.name());
        Object[] emptyArguments = arguments.toArray();
        emptyArguments[n] = Optional.empty();
        assertWireMap(absent, fieldsOf(constructor.newInstance(emptyArguments)));
      }
      // PT-PRO-001-NAMED-RANGE-001-BEGIN
      // Independent UI/SS widths verify each constructor's field/width binding, not just helper
      // code.
      if (signature.get(n) == int.class || signature.get(n) == long.class) {
        long maximum = BigInteger.TEN.pow(field.length()).subtract(BigInteger.ONE).longValueExact();
        for (int boundary = 0; boundary < 4; boundary++) {
          long value =
              switch (boundary) {
                case 0 -> 0;
                case 1 -> maximum;
                case 2 -> -1;
                default -> maximum + 1;
              };
          Object numeric;
          if (signature.get(n) == int.class) numeric = Math.toIntExact(value);
          else numeric = value;
          Object[] numericArguments = arguments.toArray();
          numericArguments[n] = numeric;
          if (boundary < ACCEPTED_NUMERIC_BOUNDARY_VECTORS) {
            Object bounded = constructor.newInstance(numericArguments);
            assertEquals(numeric, getters.get(n).invoke(bounded), field.name());
          } else {
            var failure =
                assertThrows(
                    InvocationTargetException.class,
                    () -> constructor.newInstance(numericArguments));
            var cause = assertInstanceOf(LayoutValidationException.class, failure.getCause());
            assertEquals(
                "typed numeric field is out of range: " + accessors.get(field.name()),
                cause.getMessage(),
                type.getSimpleName() + ":" + field.name());
          }
        }
      }
      // PT-PRO-001-NAMED-RANGE-001-END
      // PT-PRO-001-NAMED-FLAG-001-BEGIN
      if (signature.get(n) == boolean.class) {
        for (boolean flag : new boolean[] {false, true}) {
          Map<String, FieldValue> flagFields = new LinkedHashMap<>(input);
          flagFields.put(field.name(), new FieldValue.Flag(flag));
          Object flagged = from.invoke(null, new FieldValueSet(flagFields));
          assertEquals(Boolean.valueOf(flag), getters.get(n).invoke(flagged), field.name());
          assertWireMap(flagFields, fieldsOf(flagged));
          Object[] flagArguments = arguments.toArray();
          flagArguments[n] = flag;
          assertWireMap(flagFields, fieldsOf(constructor.newInstance(flagArguments)));
        }
      }
      // PT-PRO-001-NAMED-FLAG-001-END
    }
    var nullFailure =
        assertThrows(InvocationTargetException.class, () -> from.invoke(null, new Object[] {null}));
    assertInstanceOf(NullPointerException.class, nullFailure.getCause());
    if (fields.isEmpty()) {
      var extra =
          assertThrows(
              InvocationTargetException.class,
              () ->
                  from.invoke(
                      null, new FieldValueSet(Map.of("unknown", new FieldValue.Text("x")))));
      assertInstanceOf(LayoutValidationException.class, extra.getCause());
    }
    assertEquals(type.getSimpleName() + "[REDACTED]", decoded.toString());
    return optionals;
  }

  private static Class<?> scalarType(Field field, String layout) throws ClassNotFoundException {
    if (field.wire().equals("B")) return boolean.class;
    String semantic =
        switch (field.name()) {
          case "User ID" -> "UserId";
          case "Entry ID" -> "EntryId";
          case "Audio ID" -> "AudioId";
          case "Log ID" -> "LogId";
          case "Notification ID" -> "NotificationId";
          case "Question ID" -> "QuestionId";
          case "Script file ID", "Previous file ID", "Next file ID" -> "ScriptFileId";
          case "Speaker ID" -> "SpeakerId";
          case "Async job ID" -> "AsyncJobId";
          case "Game code" -> "GameCode";
          case "Entry type" -> "EntryType";
          case "Voice条件" -> "VoiceCondition";
          case "Disposition", "Content disposition" -> "ContentDisposition";
          case "Delivery mode" -> "DeliveryMode";
          case "Pair role" -> "PairRole";
          case "Role", "New role" -> "UserRole";
          case "Level" -> "LogLevel";
          case "Log type" -> "LogType";
          case "State" -> "UserState";
          case "内部状態", "更新後状態" -> "NotificationState";
          case "回答状態" -> "AnswerState";
          case "通知区分" -> "NotificationType";
          case "Error code" -> "NotificationErrorCode";
          case "MIME type" -> "MediaMimeType";
          case "HTTP status" -> "HttpStatusCode";
          case "Elapsed ms" -> "ElapsedMilliseconds";
          default -> "";
        };
    if (field.name().equals("Category") && field.length() == 16)
      semantic =
          layout.equals("ANLREQ01")
              ? "AnimationListCategory"
              : layout.equals("VIDRSP01") ? "VideoCategory" : "AnimationCategory";
    if (!semantic.isEmpty()) return Class.forName(SEMANTIC + semantic);
    if (field.name().equals("認証context ID")) return AuthenticationContext.class;
    if (field.name().contains("SHA-256")) return Class.forName(SEMANTIC + "Sha256Hex");
    if (field.name().endsWith("relative path")) return Class.forName(SEMANTIC + "RelativePath");
    if (field.name().endsWith("display path") || field.name().equals("Display path"))
      return Class.forName(SEMANTIC + "DisplayPath");
    if (field.length() == JST_WIRE_DIGITS) return Instant.class;
    if (field.wire().equals("N")) return field.length() <= 8 ? int.class : long.class;
    if (field.length() == UUID_TEXT_LENGTH) return UUID.class;
    return String.class;
  }

  private static FieldValue independentWire(Field field, Class<?> scalar, int index) {
    if (field.wire().equals("B")) return new FieldValue.Flag(index % 2 == 0);
    String text;
    if (ENUM_WIRE.containsKey(scalar.getSimpleName())) text = ENUM_WIRE.get(scalar.getSimpleName());
    else if (scalar == Instant.class) text = JST.format(TIME.plusMillis(index));
    else if (scalar == UUID.class) text = String.format("00000000-0000-4000-8000-%012d", index);
    else if (scalar == AuthenticationContext.class || scalar.getSimpleName().equals("Sha256Hex"))
      text = String.format("%064x", index);
    else if (scalar.getSimpleName().equals("RelativePath")
        || scalar.getSimpleName().equals("DisplayPath")) text = "fixture/item" + index + ".txt";
    else if (scalar == int.class
        || scalar == long.class
        || ProtocolId.class.isAssignableFrom(scalar)
        || scalar.getSimpleName().equals("ElapsedMilliseconds")) text = Integer.toString(index);
    else if (scalar.getSimpleName().equals("HttpStatusCode")) text = Integer.toString(200 + index);
    else
      text =
          switch (field.name()) {
            case "Client address", "Remote address" -> "192.0.2." + index;
            case "受付ID" -> String.format("%026d", index);
            case "Password", "Initial Password", "New Password" -> "PublicFixture" + index + "!";
            case "HTTP method" -> "POST";
            case "Path" -> "/fixture/" + index;
            case "Details" -> "{\"fixture\":" + index + "}";
            default -> "fixture" + index;
          };
    return field.wire().equals("N")
        ? new FieldValue.Numeric(Long.parseLong(text))
        : new FieldValue.Text(text);
  }

  private static Object independentInput(Class<?> scalar, FieldValue wire, int index)
      throws Exception {
    String text =
        wire instanceof FieldValue.Text value
            ? value.value()
            : wire instanceof FieldValue.Numeric value ? Long.toString(value.value()) : "";
    if (scalar == String.class) return text;
    if (scalar == boolean.class) return ((FieldValue.Flag) wire).value();
    if (scalar == int.class) return Integer.parseInt(text);
    if (scalar == long.class) return Long.parseLong(text);
    if (scalar == Instant.class) return TIME.plusMillis(index);
    if (scalar == UUID.class) return UUID.fromString(text);
    if (ENUM_MEMBERS.containsKey(scalar.getSimpleName()))
      return scalar.getField(ENUM_MEMBERS.get(scalar.getSimpleName())).get(null);
    if (ProtocolId.class.isAssignableFrom(scalar))
      return scalar.getConstructor(long.class).newInstance(Long.parseLong(text));
    if (scalar.getSimpleName().equals("HttpStatusCode")
        || scalar.getSimpleName().equals("ElapsedMilliseconds"))
      return scalar.getConstructor(int.class).newInstance(Integer.parseInt(text));
    // A Production factory here constructs actual INPUT only. Expected wire/scalar
    // values above remain literals/standard Java arithmetic, never its output.
    return scalar.getMethod("of", String.class).invoke(null, text);
  }

  private static void assertScalar(FieldValue wire, Object actual, int index, String context)
      throws Exception {
    assertNotNull(actual, context);
    if (actual instanceof Instant) {
      assertEquals(TIME.plusMillis(index), actual, context);
      return;
    }
    if (actual instanceof ProtocolId value) {
      assertEquals(number(wire), value.value(), context);
      return;
    }
    if (actual instanceof Number value) {
      assertEquals(number(wire), value.longValue(), context);
      return;
    }
    if (actual instanceof UUID value) {
      assertEquals(((FieldValue.Text) wire).value(), value.toString(), context);
      return;
    }
    if (actual instanceof Boolean value) {
      assertEquals(((FieldValue.Flag) wire).value(), value, context);
      return;
    }
    if (actual instanceof String value) {
      assertEquals(((FieldValue.Text) wire).value(), value, context);
      return;
    }
    if (actual instanceof WireEnum value) {
      assertEquals(((FieldValue.Text) wire).value(), value.wireValue(), context);
      return;
    }
    assertEquals(
        ((FieldValue.Text) wire).value(),
        actual.getClass().getMethod("wireValue").invoke(actual),
        context);
  }

  private static long number(FieldValue value) {
    return value instanceof FieldValue.Numeric numeric
        ? numeric.value()
        : Long.parseLong(((FieldValue.Text) value).value());
  }

  private static FieldValueSet fieldsOf(Object object) {
    if (object instanceof PayloadData data) return data.fields();
    return ((PayloadRecord) object).fields();
  }

  private static void assertWireMap(Map<String, FieldValue> expected, FieldValueSet actual) {
    assertEquals(expected.keySet(), actual.names());
    expected.forEach((name, value) -> assertEquals(value, actual.getOrUnset(name), name));
  }

  private static List<String[]> fixture(String name) throws Exception {
    try (var input = IndependentNamedFieldOracle.class.getResourceAsStream("/protocol/" + name)) {
      assertNotNull(input, name);
      try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
        return reader
            .lines()
            .filter(line -> !line.isBlank() && !line.startsWith("#"))
            .map(line -> line.split("\t", -1))
            .toList();
      }
    }
  }

  private record Field(String name, int length, String wire, String presence) {
    boolean optional() {
      return wire.equals("X") && (presence.equals("C") || presence.equals("O"));
    }
  }
}
