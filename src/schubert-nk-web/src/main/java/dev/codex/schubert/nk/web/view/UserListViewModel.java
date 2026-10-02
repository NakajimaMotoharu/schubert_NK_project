package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/**
 * Display-only, C-byte order, no response repair. SCR015/UI225,236/SS313,332;
 * PG-D344/PT-USER-HTTP006..010.
 */
@NullMarked
public final class UserListViewModel {
  private final TopBarViewModel topBar;
  private final UserSearchForm filters;
  private final Optional<PageViewModel> page;
  private final List<Row> rows;

  private UserListViewModel(
      SessionPrincipal actor,
      UserSearchForm form,
      Optional<PageViewModel> page,
      List<UserRecord> rows) {
    if (Objects.requireNonNull(actor, "actor").role() != UserRole.ADMIN)
      throw new IllegalArgumentException("user display requires administrator");
    topBar = TopBarViewModel.from(actor);
    filters = Objects.requireNonNull(form, "form");
    this.page = page;
    this.rows = List.copyOf(rows.stream().map(Row::new).toList());
  }

  public static UserListViewModel success(
      SessionPrincipal actor,
      UserSearchForm form,
      PagedResponseData data,
      List<UserRecord> records) {
    Objects.requireNonNull(form, "form");
    if (!form.isValid()) throw new IllegalArgumentException("invalid successful user form");
    var page = PageViewModel.from(data, 50);
    if (page.getEffectivePage() != Math.min(form.getPage(), page.getTotalPages()))
      throw new IllegalArgumentException("user response page does not match request");
    var copy = List.copyOf(records);
    long expected = page.isEmpty() ? 0 : page.getLastResult() - page.getFirstResult() + 1;
    if (copy.size() != expected)
      throw new IllegalArgumentException("inconsistent user record count");
    var ids = new HashSet<Long>();
    for (int i = 0; i < copy.size(); i++) {
      var current = copy.get(i);
      if (!ids.add(current.userId().value()))
        throw new IllegalArgumentException("duplicate user identity");
      if (i > 0) {
        var previous = copy.get(i - 1);
        int order =
            Arrays.compareUnsigned(
                previous.username().getBytes(StandardCharsets.UTF_8),
                current.username().getBytes(StandardCharsets.UTF_8));
        if (order > 0 || (order == 0 && previous.userId().value() >= current.userId().value()))
          throw new IllegalArgumentException("invalid user display order");
      }
    }
    return new UserListViewModel(actor, form, Optional.of(page), copy);
  }

  public static UserListViewModel invalid(SessionPrincipal actor, UserSearchForm form) {
    Objects.requireNonNull(form, "form");
    if (form.isValid()) throw new IllegalArgumentException("valid form used as invalid");
    return new UserListViewModel(actor, form, Optional.empty(), List.of());
  }

  private String link(int number) {
    return "/admin/users?username="
        + encode(filters.getUsername())
        + "&role="
        + encode(filters.getRole())
        + "&state="
        + encode(filters.getState())
        + "&page="
        + number;
  }

  private static String encode(String value) {
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public Optional<String> getPreviousHref() {
    return page.flatMap(
        value ->
            value.getPreviousPage().isPresent()
                ? Optional.of(link(value.getPreviousPage().getAsInt()))
                : Optional.empty());
  }

  public Optional<String> getNextHref() {
    return page.flatMap(
        value ->
            value.getNextPage().isPresent()
                ? Optional.of(link(value.getNextPage().getAsInt()))
                : Optional.empty());
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public UserSearchForm getFilters() {
    return filters;
  }

  public Optional<PageViewModel> getPage() {
    return page;
  }

  public List<Row> getRows() {
    return rows;
  }

  @Override
  public String toString() {
    return "UserListViewModel[REDACTED]";
  }

  public static final class Row {
    private static final DateTimeFormatter TIME =
        DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSS", Locale.ROOT)
            .withZone(ZoneOffset.ofHours(9));
    private final long id;
    private final String username, role, state, lockedUntil, lastLogin, createdAt, updatedAt;

    private Row(UserRecord value) {
      id = value.userId().value();
      username = value.username();
      role = value.role().wireValue();
      state = value.state().wireValue();
      lockedUntil = value.lockedUntil().map(Row::time).orElse("");
      lastLogin = value.lastLogin().map(Row::time).orElse("");
      createdAt = time(value.createdAt());
      updatedAt = time(value.updatedAt());
    }

    private static String time(Instant value) {
      return TIME.format(value);
    }

    public long getId() {
      return id;
    }

    public String getDetailHref() {
      return "/admin/users/" + id;
    }

    public String getUsername() {
      return username;
    }

    public String getRole() {
      return role;
    }

    public String getState() {
      return state;
    }

    public String getLockedUntil() {
      return lockedUntil;
    }

    public String getLastLogin() {
      return lastLogin;
    }

    public String getCreatedAt() {
      return createdAt;
    }

    public String getUpdatedAt() {
      return updatedAt;
    }

    @Override
    public String toString() {
      return "UserListRow[REDACTED]";
    }
  }
}
