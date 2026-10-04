package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.PayloadData;
import java.util.Map;
import org.jspecify.annotations.NullMarked;

/** Closed four existing SCR017 forms, not a general binding framework. SSC177/PG-D366/081. */
@NullMarked
public sealed interface UserChangeForm extends AutoCloseable
    permits UserStatusForm, UserRoleForm, PasswordResetForm, UserUnlockForm {
  boolean isValid();

  Map<String, String> getIssues();

  Map<String, Object> displayValues();

  PayloadData toRequest();

  @Override
  void close();
}
