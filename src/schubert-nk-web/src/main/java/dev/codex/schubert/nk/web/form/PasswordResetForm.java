package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR017/FUN009/AUT002003/UI225236/SS313314; PG-D353/PT-USER-CHANGE001..016. */
@NullMarked
public final class PasswordResetForm implements AutoCloseable {
  private final UserMutationInput input;

  private PasswordResetForm(UserMutationInput input) {
    this.input = input;
  }

  /** targetUsername comes from the authenticated fresh API user detail, never HTTP parameters. */
  public static PasswordResetForm bind(
      long pathId, String targetUsername, Map<String, List<String>> parameters) {
    return new PasswordResetForm(
        UserMutationInput.bind("PASSWORD", pathId, targetUsername, parameters));
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

  /** Returned String DTO is separately owned; close cannot erase its immutable string. */
  public PasswordResetRequestData toRequest() {
    input.requireUsable();
    return new PasswordResetRequestData(
        new UserId(input.id), input.password(), input.version, input.token);
  }

  @Override
  public void close() {
    input.close();
  }

  @Override
  public String toString() {
    return "PasswordResetForm[REDACTED]";
  }
}
