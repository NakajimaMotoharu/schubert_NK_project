package dev.codex.schubert.nk.web.form;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Closed SCR017 binding only; FUN009/AUT002003/UI225236/SS313314; PG-D353/016069. */
@NullMarked
final class UserMutationInput implements AutoCloseable {
  private static final String INVALID = "入力項目を確認してください。";
  private static final Set<String> COMMON =
      Set.of("operation", "id", "expected_version", "confirm", "operation_token");
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
  final long id, version;
  final UUID token;
  final boolean enabled;
  final String role;
  private final char[] password;
  final Map<String, String> issues;
  private boolean closed;

  private UserMutationInput(
      long id,
      long version,
      UUID token,
      boolean enabled,
      String role,
      char[] password,
      Map<String, String> issues) {
    this.id = id;
    this.version = version;
    this.token = token;
    this.enabled = enabled;
    this.role = role;
    this.password = password.clone();
    this.issues = Map.copyOf(issues);
  }

  static UserMutationInput bind(
      String operation, long pathId, String targetUsername, Map<String, List<String>> parameters) {
    Objects.requireNonNull(operation, "operation");
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
          if (copy.size() != 1) issues.put("form", INVALID);
          else values.put(key, copy.getFirst());
        });
    for (String name : permitted) {
      if (!values.containsKey(name)) {
        values.put(name, "");
        issues.put(name, INVALID);
      }
    }
    if (!operation.equals(values.get("operation"))) issues.put("operation", INVALID);
    String identifier = Objects.requireNonNull(values.get("id"));
    if (!identifier.matches("[0-9]{1,12}") || Long.parseLong(identifier) != pathId)
      issues.put("id", INVALID);
    String expected = Objects.requireNonNull(values.get("expected_version"));
    long version = 0;
    if (!expected.matches("[0-9]{1,9}")) issues.put("expected_version", INVALID);
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
    char[] password = normalized.toCharArray();
    byte[] bytes = normalized.getBytes(StandardCharsets.UTF_8);
    try {
      if (operation.equals("PASSWORD")) {
        int count = normalized.codePointCount(0, normalized.length());
        String account = Normalizer.normalize(targetUsername.trim(), Normalizer.Form.NFC);
        if (count < 12
            || count > 128
            || bytes.length > 256
            || normalized.endsWith(" ")
            || normalized.codePoints().anyMatch(UserMutationInput::invalidCharacter)
            || normalized.equalsIgnoreCase(account)) issues.put("password", INVALID);
        String confirmation =
            Normalizer.normalize(
                Objects.requireNonNull(values.get("password_confirmation")), Normalizer.Form.NFC);
        if (!normalized.equals(confirmation)) issues.put("password_confirmation", INVALID);
      }
      if (!issues.isEmpty()) Arrays.fill(password, '\0');
      return new UserMutationInput(
          pathId, version, token, flag.equals("true"), role, password, issues);
    } finally {
      Arrays.fill(password, '\0');
      Arrays.fill(bytes, (byte) 0);
    }
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
    return new String(password);
  }

  Map<String, Object> displayValues() {
    requireOpen();
    return Map.of("id", id, "expected_version", version);
  }

  private void requireOpen() {
    if (closed) throw new IllegalStateException("user mutation form is closed");
  }

  @Override
  public void close() {
    Arrays.fill(password, '\0');
    closed = true;
  }

  @Override
  public String toString() {
    return "UserMutationInput[REDACTED]";
  }
}
