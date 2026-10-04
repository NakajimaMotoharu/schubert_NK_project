package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Display only SCR017/UI225,236/SS313,314; PG-D346/PT-USER-DETAIL001..008. */
@NullMarked
public final class UserDetailViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSS", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private final TopBarViewModel topBar;
  private final Map<String, Object> values;

  private UserDetailViewModel(SessionPrincipal actor, UserDetailResponseData data) {
    topBar = TopBarViewModel.from(actor);
    values =
        Map.copyOf(
            Map.ofEntries(
                Map.entry("id", data.userId().value()),
                Map.entry("username", data.username()),
                Map.entry("role", data.role().wireValue()),
                Map.entry("state", data.state().wireValue()),
                Map.entry("lockReason", data.state() == UserState.LOCKED ? "ログイン失敗によるロック" : ""),
                Map.entry(
                    "lockedUntil", data.lockedUntil().map(UserDetailViewModel::time).orElse("")),
                Map.entry("lastLogin", data.lastLogin().map(UserDetailViewModel::time).orElse("")),
                Map.entry("passwordChangedAt", time(data.passwordChangedAt())),
                Map.entry("createdAt", time(data.createdAt())),
                Map.entry("updatedAt", time(data.updatedAt())),
                Map.entry("activeSessionCount", data.activeSessionCount()),
                Map.entry("version", data.version()),
                Map.entry("createdBy", data.createdBy()),
                Map.entry("updatedBy", data.updatedBy()),
                Map.entry("self", actor.username().equalsIgnoreCase(data.username()))));
  }

  public static UserDetailViewModel from(
      SessionPrincipal actor, UserId requested, UserDetailResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(requested, "requested");
    Objects.requireNonNull(data, "data");
    if (actor.role() != UserRole.ADMIN
        || !requested.equals(data.userId())
        || data.activeSessionCount() > 2)
      throw new IllegalArgumentException("invalid user detail projection");
    // BUG639/YKT452: the typed N9 version already permits 0, including newly created users.
    return new UserDetailViewModel(actor, data);
  }

  private static String time(Instant value) {
    return TIME.format(value);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "UserDetailViewModel[REDACTED]";
  }
}
