package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.util.List;
import java.util.Map;
import org.jspecify.annotations.NullMarked;

/** SCR022023/FUN013/QST; UI224236; SS313314323; PG-D368/PT-TARGET001..008. */
@NullMarked
public final class QuestionDeleteForm {
  private final TargetOperationInput input;

  private QuestionDeleteForm(TargetOperationInput input) {
    this.input = input;
  }

  public static QuestionDeleteForm bind(long pathId, Map<String, List<String>> parameters) {
    return new QuestionDeleteForm(TargetOperationInput.bind("DELETE", pathId, parameters));
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

  public QuestionDeleteRequestData toRequest() {
    input.requireValid();
    return new QuestionDeleteRequestData(new QuestionId(input.id), input.token);
  }

  @Override
  public String toString() {
    return "QuestionDeleteForm[REDACTED]";
  }
}
