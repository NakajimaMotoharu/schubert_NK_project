package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR017/FUN009/AUT002003/UI225236/SS313314; PG-D353/PT-USER-CHANGE001..016. */
@NullMarked
public final class UserStatusForm implements AutoCloseable {
  private final UserMutationInput input;

  private UserStatusForm(UserMutationInput input) {
    this.input = input;
  }

  public static UserStatusForm bind(long pathId, Map<String, List<String>> parameters) {
    return new UserStatusForm(UserMutationInput.bind("STATUS", pathId, "", parameters));
  }

  public boolean isValid() {
    return input.isValid();
  }

  public Map<String, String> getIssues() {
    return input.issues;
  }

  public Map<String, Object> displayValues() {
    var values = new HashMap<>(input.displayValues());
    values.put("enabled", input.enabled);
    return Map.copyOf(values);
  }

  /** Caller verifies session/purpose token; API independently enforces self/admin/version. */
  public UserStatusRequestData toRequest() {
    input.requireUsable();
    return new UserStatusRequestData(
        new UserId(input.id), input.enabled, input.version, input.token);
  }

  @Override
  public void close() {
    input.close();
  }

  @Override
  public String toString() {
    return "UserStatusForm[REDACTED]";
  }
}
