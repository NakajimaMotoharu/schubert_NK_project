package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR021/FUN010/NTF; UI224236; SS313314323; PG-D368/PT-TARGET001..008. */
@NullMarked
public final class CancelForm {
  private final TargetOperationInput input;

  private CancelForm(TargetOperationInput input) {
    this.input = input;
  }

  public static CancelForm bind(long pathId, Map<String, List<String>> parameters) {
    return new CancelForm(TargetOperationInput.bind("CANCEL", pathId, parameters));
  }

  public boolean isValid() {
    return input.issues.isEmpty();
  }

  public Map<String, String> getIssues() {
    return input.issues;
  }

  public Map<String, Object> displayValues() {
    return input.values;
  }

  public NotificationCancelRequestData toRequest() {
    input.requireValid();
    return new NotificationCancelRequestData(new NotificationId(input.id), input.token);
  }

  @Override
  public String toString() {
    return "CancelForm[REDACTED]";
  }
}
