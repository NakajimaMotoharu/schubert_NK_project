package dev.codex.schubert.nk.web.form;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Closed SCR017 binding only; FUN009/AUT002003/UI225236/SS313314; PG-D353/016069. */
@NullMarked
final class UserMutationInput implements AutoCloseable {
  private static final int SINGLE_PARAMETER_VALUE_COUNT = 1;

  private static final java.lang.String LITERAL_OPERATION = "operation";

  private static final java.lang.String LITERAL_EXPECTED_VERSION = "expected_version";

  private static final String INVALID = "入力項目を確認してください。";
  private static final Set<String> COMMON =
      Set.of(LITERAL_OPERATION, "id", LITERAL_EXPECTED_VERSION, "confirm", "operation_token");
  private static final Map<String, Set<String>> EXTRA =
      Map.of(
          "STATUS",
          Set.of("enabled"),
          "ROLE",
          Set.of("role"),
          "PASSWORD",
          Set.of("password", "password_confirmation"),
          "UNLOCK",
          Set.of());
  final long id;
  final long version;
  final UUID token;
  final boolean enabled;
  final String role;
  private final char[] retainedPassword;
  final Map<String, String> issues;
  private boolean closed;

  private UserMutationInput(
      long id,
      long version,
      UUID token,
      boolean enabled,
      String role,
      String password,
      Map<String, String> issues) {
    this.id = id;
    this.version = version;
    this.token = token;
    this.enabled = enabled;
    this.role = role;
    this.issues = Map.copyOf(issues);
    this.retainedPassword = this.issues.isEmpty() ? password.toCharArray() : new char[0];
  }

  static UserMutationInput bind(
      String operation, long pathId, String targetUsername, Map<String, List<String>> parameters) {
    Objects.requireNonNull(operation, LITERAL_OPERATION);
    Objects.requireNonNull(targetUsername, "targetUsername");
    Objects.requireNonNull(parameters, "parameters");
    Set<String> extra = EXTRA.get(operation);
    if (extra == null) throw new IllegalArgumentException("unsupported user operation");
    if (pathId < 1 || pathId > 999999999999L)
      throw new IllegalArgumentException("invalid user path identifier");
    if (operation.equals("PASSWORD") && targetUsername.isBlank())
      throw new IllegalArgumentException("missing verified target username");
    var permitted = new HashSet<>(COMMON);
    permitted.addAll(extra);
    var issues = new HashMap<String, String>();
    var values = new HashMap<String, String>();
    parameters.forEach(
        (key, value) -> {
          Objects.requireNonNull(key, "name");
          List<String> copy = List.copyOf(value);
          if (!permitted.contains(key) && !key.equals("_csrf")) issues.put("form", INVALID);
          if (copy.size() != SINGLE_PARAMETER_VALUE_COUNT) issues.put("form", INVALID);
          else values.put(key, copy.getFirst());
        });
    for (String name : permitted) {
      if (!values.containsKey(name)) {
        values.put(name, "");
        issues.put(name, INVALID);
      }
    }
    if (!operation.equals(values.get(LITERAL_OPERATION))) issues.put(LITERAL_OPERATION, INVALID);
    String identifier = Objects.requireNonNull(values.get("id"));
    if (!identifier.matches("[0-9]{1,12}") || Long.parseLong(identifier) != pathId)
      issues.put("id", INVALID);
    String expected = Objects.requireNonNull(values.get(LITERAL_EXPECTED_VERSION));
    long version = 0;
    if (!expected.matches("[0-9]{1,9}")) issues.put(LITERAL_EXPECTED_VERSION, INVALID);
    else version = Long.parseLong(expected);
    if (!"true".equals(values.get("confirm"))) issues.put("confirm", INVALID);
    UUID token = new UUID(0, 0);
    String text = Objects.requireNonNull(values.get("operation_token"));
    if (!text.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))
      issues.put("operation_token", INVALID);
    else token = UUID.fromString(text);
    String flag = values.getOrDefault("enabled", "false");
    if (operation.equals("STATUS") && !Set.of("true", "false").contains(flag))
      issues.put("enabled", INVALID);
    String role = values.getOrDefault("role", "USER");
    if (operation.equals("ROLE") && !Set.of("USER", "ADMIN").contains(role)) {
      issues.put("role", INVALID);
      role = "USER";
    }
    String normalized =
        Normalizer.normalize(values.getOrDefault("password", ""), Normalizer.Form.NFC);
    byte[] bytes = normalized.getBytes(StandardCharsets.UTF_8);
    int byteLength = bytes.length;
    // No secret byte buffer remains live during validation or construction (BUG3196).
    Arrays.fill(bytes, (byte) 0);
    if (operation.equals("PASSWORD")) {
      int count = normalized.codePointCount(0, normalized.length());
      String account = Normalizer.normalize(targetUsername.trim(), Normalizer.Form.NFC);
      if (count < 12
          || count > 128
          || byteLength > 256
          || normalized.endsWith(" ")
          || normalized.codePoints().anyMatch(UserMutationInput::invalidCharacter)
          || normalized.equalsIgnoreCase(account)) issues.put("password", INVALID);
      String confirmation =
          Normalizer.normalize(
              Objects.requireNonNull(values.get("password_confirmation")), Normalizer.Form.NFC);
      if (!normalized.equals(confirmation)) issues.put("password_confirmation", INVALID);
    }
    return new UserMutationInput(
        pathId, version, token, flag.equals("true"), role, normalized, issues);
  }

  private static boolean invalidCharacter(int value) {
    return Character.isISOControl(value)
        || (value >= Character.MIN_SURROGATE && value <= Character.MAX_SURROGATE);
  }

  boolean isValid() {
    return issues.isEmpty();
  }

  void requireUsable() {
    if (closed) throw new IllegalStateException("user mutation form is closed");
    if (!isValid()) throw new IllegalArgumentException("invalid user mutation form");
  }

  String password() {
    requireUsable();
    return new String(retainedPassword);
  }

  Map<String, Object> displayValues() {
    requireOpen();
    return Map.of("id", id, LITERAL_EXPECTED_VERSION, version);
  }

  private void requireOpen() {
    if (closed) throw new IllegalStateException("user mutation form is closed");
  }

  @Override
  public void close() {
    Arrays.fill(retainedPassword, '\0');
    closed = true;
  }

  @Override
  public String toString() {
    return "UserMutationInput[REDACTED]";
  }
}
