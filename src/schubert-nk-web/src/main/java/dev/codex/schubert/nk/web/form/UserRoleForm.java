package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR017/FUN009/AUT002003/UI225236/SS313314; PG-D353/PT-USER-CHANGE001..016. */
@NullMarked
public final class UserRoleForm implements UserChangeForm {
  private final UserMutationInput input;

  private UserRoleForm(UserMutationInput input) {
    this.input = input;
  }

  public static UserRoleForm bind(long pathId, Map<String, List<String>> parameters) {
    return new UserRoleForm(UserMutationInput.bind("ROLE", pathId, "", parameters));
  }

  public boolean isValid() {
    return input.isValid();
  }

  public Map<String, String> getIssues() {
    return input.issues;
  }

  public Map<String, Object> displayValues() {
    var values = new HashMap<>(input.displayValues());
    values.put("role", input.role);
    return Map.copyOf(values);
  }

  /** Caller verifies session/purpose token; latest/last ADMIN checks remain in the API. */
  public UserRoleRequestData toRequest() {
    input.requireUsable();
    return new UserRoleRequestData(
        new UserId(input.id), UserRole.valueOf(input.role), input.version, input.token);
  }

  @Override
  public void close() {
    input.close();
  }

  @Override
  public String toString() {
    return "UserRoleForm[REDACTED]";
  }
}
