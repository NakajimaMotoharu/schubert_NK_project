package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** SCR016/FUN009/AUT002/UI225,236/SS313,314; PG-D345/PT-USER-CREATE001..008. */
@NullMarked
public final class UserCreateForm implements AutoCloseable {
  private static final int SINGLE_PARAMETER_VALUE_COUNT = 1;

  private static final java.lang.String LITERAL_USERNAME = "username";

  private static final java.lang.String LITERAL_ROLE = "role";

  private static final java.lang.String LITERAL_ENABLED = "enabled";

  private static final Set<String> FIELDS =
      Set.of(
          LITERAL_USERNAME,
          "password",
          "password_confirmation",
          LITERAL_ROLE,
          LITERAL_ENABLED,
          "operation_token");
  private static final String INVALID = "入力項目を確認してください。";
  private final String username;
  private final String role;
  private final boolean enabled;
  private final UUID operationToken;
  private final char[] password;
  private final Map<String, String> issues;
  private boolean closed;

  private UserCreateForm(
      String username,
      String role,
      boolean enabled,
      UUID operationToken,
      String password,
      Map<String, String> issues) {
    this.username = username;
    this.role = role;
    this.enabled = enabled;
    this.operationToken = operationToken;
    this.issues = Map.copyOf(issues);
    this.password = this.issues.isEmpty() ? password.toCharArray() : new char[0];
  }

  /** CSRF is validated by the existing security filter, never retained by this form. */
  public static UserCreateForm bind(Map<String, List<String>> parameters) {
    Objects.requireNonNull(parameters, "parameters");
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var issues = new HashMap<String, String>();
    var values = new HashMap<String, String>();
    for (var entry : snapshot.entrySet()) {
      if (!FIELDS.contains(entry.getKey()) && !entry.getKey().equals("_csrf"))
        issues.put("form", INVALID);
      if (entry.getValue().size() != SINGLE_PARAMETER_VALUE_COUNT) issues.put("form", INVALID);
    }
    for (String name : FIELDS) {
      List<String> input = snapshot.getOrDefault(name, List.of());
      if (input.size() == SINGLE_PARAMETER_VALUE_COUNT) values.put(name, input.getFirst());
      else {
        values.put(name, "");
        issues.put(name, INVALID);
      }
    }
    String username =
        Normalizer.normalize(
                Objects.requireNonNull(values.get(LITERAL_USERNAME)), Normalizer.Form.NFC)
            .trim();
    if (!username.matches("[A-Za-z0-9._-]+")
        || username.getBytes(StandardCharsets.UTF_8).length > 64) {
      issues.put(LITERAL_USERNAME, INVALID);
      username = "";
    }
    String role = Objects.requireNonNull(values.get(LITERAL_ROLE));
    if (!Set.of("USER", "ADMIN").contains(role)) {
      issues.put(LITERAL_ROLE, INVALID);
      role = "USER";
    }
    String flag = Objects.requireNonNull(values.get(LITERAL_ENABLED));
    if (!Set.of("true", "false").contains(flag)) issues.put(LITERAL_ENABLED, INVALID);
    UUID token = new UUID(0, 0);
    String text = Objects.requireNonNull(values.get("operation_token"));
    if (!text.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))
      issues.put("operation_token", INVALID);
    else token = UUID.fromString(text);
    String normalized =
        Normalizer.normalize(Objects.requireNonNull(values.get("password")), Normalizer.Form.NFC);
    String confirmation =
        Normalizer.normalize(
            Objects.requireNonNull(values.get("password_confirmation")), Normalizer.Form.NFC);
    byte[] bytes = normalized.getBytes(StandardCharsets.UTF_8);
    int byteLength = bytes.length;
    // End temporary byte ownership before validation or construction can fail (BUG3196).
    Arrays.fill(bytes, (byte) 0);
    int count = normalized.codePointCount(0, normalized.length());
    if (count < 12
        || count > 128
        || byteLength > 256
        || normalized.endsWith(" ")
        || normalized.codePoints().anyMatch(UserCreateForm::invalidCharacter)
        || normalized.equalsIgnoreCase(username)) issues.put("password", INVALID);
    if (!normalized.equals(confirmation)) issues.put("password_confirmation", INVALID);
    return new UserCreateForm(username, role, flag.equals("true"), token, normalized, issues);
  }

  private static boolean invalidCharacter(int value) {
    return Character.isISOControl(value)
        || (value >= Character.MIN_SURROGATE && value <= Character.MAX_SURROGATE);
  }

  public boolean isValid() {
    return issues.isEmpty();
  }

  /** This is the complete redisplay projection; passwords, CSRF and operation token are absent. */
  public Map<String, Object> displayValues() {
    return Map.of(LITERAL_USERNAME, username, LITERAL_ROLE, role, LITERAL_ENABLED, enabled);
  }

  public Map<String, String> getIssues() {
    return issues;
  }

  /** The caller must independently bind the token to the current session and CREATE purpose. */
  public UserCreateRequestData toRequest() {
    if (closed) throw new IllegalStateException("user create form is closed");
    if (!isValid()) throw new IllegalArgumentException("invalid user create form");
    return new UserCreateRequestData(
        username, new String(password), UserRole.valueOf(role), enabled, operationToken);
  }

  @Override
  public void close() {
    Arrays.fill(password, '\0');
    closed = true;
  }

  @Override
  public String toString() {
    return "UserCreateForm[REDACTED]";
  }
}
