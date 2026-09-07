package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.auth.LoginResponseData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * API result to fixed DATA; caller retains matching result code for the response header.
 * NK-AUT-001; FUN-001/MQ-021; UI222/234; SS312/322/323/314; PT-AUT-WIRE-001..003. Error fields must
 * use result-aware codec (BUG-023/SSC-012), not success typed semantics.
 */
public final class AuthenticationResponseMapper {
  private static final LayoutId LOGIN = new LayoutId("LGNRSP01");
  private static final LayoutId LOGOUT = new LayoutId("LOGRSP01");

  public FixedPayload login(LoginResult result) {
    Objects.requireNonNull(result, "result");
    if (result instanceof LoginResult.Success success) {
      var data =
          new LoginResponseData(
              Optional.of(success.actor().username()),
              Optional.of(success.actor().role() == Role.ADMIN ? UserRole.ADMIN : UserRole.USER),
              Optional.of(success.issued().context()),
              Optional.of(success.issued().issuedAt()),
              Optional.of(success.issued().expiresAt()),
              0,
              0,
              Optional.empty());
      return PayloadCodec.standard()
          .encode(
              PayloadTypeCatalog.encode(new TypedPayloadValues(LOGIN, data, List.of())),
              result.resultCode());
    }
    return loginError(
        result.resultCode(),
        result.retryAfterSeconds(),
        result.resultCode() == ResultCode.LOCKED
            ? "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。"
            : "ユーザー名またはパスワードが正しくありません。");
  }

  public FixedPayload temporaryLoginFailure() {
    return loginError(ResultCode.TEMPORARY_FAILURE, 0, "現在処理できません。しばらくしてから再操作してください。");
  }

  public FixedPayload logout(RevokedContext result) {
    Objects.requireNonNull(result, "result");
    return PayloadCodec.standard()
        .encode(
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(
                    LOGOUT, new LogoutResponseData(result.revokedAt()), List.of())),
            result.resultCode());
  }

  private static FixedPayload loginError(ResultCode code, int retry, String message) {
    return PayloadCodec.standard()
        .encode(
            new PayloadValues(
                LOGIN,
                new FieldValueSet(
                    Map.of(
                        "Retry after秒", new FieldValue.Numeric(retry),
                        "利用者message", new FieldValue.Text(message))),
                List.of()),
            code);
  }
}
