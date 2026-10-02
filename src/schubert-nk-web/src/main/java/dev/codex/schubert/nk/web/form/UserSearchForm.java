package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR015/FUN009/AUT002/UI222,225,236/SS313,332; PG-D344/PT-USER-HTTP001..010. */
@NullMarked
public final class UserSearchForm {
  private static final Set<String> FIELDS = Set.of("username", "role", "state", "page");
  private static final String INVALID = "入力項目を確認してください。";
  private final Map<String, String> values, issues;
  private final int page;

  private UserSearchForm(Map<String, String> values, Map<String, String> issues, int page) {
    this.values = Map.copyOf(values);
    this.issues = Map.copyOf(issues);
    this.page = page;
  }

  public static UserSearchForm bind(Map<String, List<String>> parameters) {
    Objects.requireNonNull(parameters, "parameters");
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var values = new HashMap<String, String>();
    var issues = new HashMap<String, String>();
    if (!FIELDS.containsAll(snapshot.keySet())) issues.put("form", INVALID);
    for (String name : FIELDS) {
      var input = snapshot.getOrDefault(name, List.of(""));
      String value = "";
      if (input.size() != 1) issues.put(name, INVALID);
      else {
        String raw = input.getFirst();
        if (raw.codePoints().anyMatch(UserSearchForm::invalidCharacter)) issues.put(name, INVALID);
        else value = Normalizer.normalize(raw, Normalizer.Form.NFC).trim();
      }
      values.put(name, value);
    }
    String username = Objects.requireNonNull(values.get("username"));
    if (username.getBytes(StandardCharsets.UTF_8).length > 64)
      issues.put("username", "UsernameはUTF-8で64 byte以内にしてください。");
    if (!Set.of("", "USER", "ADMIN").contains(values.get("role"))) issues.put("role", INVALID);
    if (!Set.of("", "ACTIVE", "DISABLED", "LOCKED").contains(values.get("state")))
      issues.put("state", INVALID);
    String text = Objects.requireNonNull(values.get("page"));
    int page = 1;
    if (!text.isEmpty()) {
      if (!text.matches("-?[0-9]+")) issues.put("page", INVALID);
      else {
        try {
          int number = Integer.parseInt(text);
          if (number > 999999) issues.put("page", INVALID);
          else page = Math.max(1, number);
        } catch (NumberFormatException failure) {
          issues.put("page", INVALID);
        }
      }
    }
    return new UserSearchForm(values, issues, page);
  }

  private static boolean invalidCharacter(int value) {
    return Character.isISOControl(value)
        || (value >= Character.MIN_SURROGATE && value <= Character.MAX_SURROGATE);
  }

  public boolean isValid() {
    return issues.isEmpty();
  }

  public String getUsername() {
    return Objects.requireNonNull(values.get("username"));
  }

  public String getRole() {
    return Objects.requireNonNull(values.get("role"));
  }

  public String getState() {
    return Objects.requireNonNull(values.get("state"));
  }

  public int getPage() {
    return page;
  }

  public Map<String, String> getIssues() {
    return issues;
  }

  public UserSearchRequestData toRequest() {
    if (!isValid()) throw new IllegalArgumentException("invalid user search form");
    return new UserSearchRequestData(
        getUsername().isEmpty() ? Optional.empty() : Optional.of(getUsername()),
        getRole().isEmpty() ? Optional.empty() : Optional.of(UserRole.valueOf(getRole())),
        getState().isEmpty() ? Optional.empty() : Optional.of(UserState.valueOf(getState())),
        page,
        50);
  }

  @Override
  public String toString() {
    return "UserSearchForm[REDACTED]";
  }
}
