package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR017/FUN009/AUT002003/UI225236/SS313314; PG-D353/PT-USER-CHANGE001..016. */
@NullMarked
public final class UserUnlockForm implements AutoCloseable {
  private final UserMutationInput input;

  private UserUnlockForm(UserMutationInput input) {
    this.input = input;
  }

  public static UserUnlockForm bind(long pathId, Map<String, List<String>> parameters) {
    return new UserUnlockForm(UserMutationInput.bind("UNLOCK", pathId, "", parameters));
  }

  public boolean isValid() {
    return input.isValid();
  }

  public Map<String, String> getIssues() {
    return input.issues;
  }

  public Map<String, Object> displayValues() {
    return input.displayValues();
  }

  public UserUnlockRequestData toRequest() {
    input.requireUsable();
    return new UserUnlockRequestData(new UserId(input.id), input.version, input.token);
  }

  @Override
  public void close() {
    input.close();
  }

  @Override
  public String toString() {
    return "UserUnlockForm[REDACTED]";
  }
}
