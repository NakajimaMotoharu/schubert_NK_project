package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * Immutable USER7/ADMIN9 menu projection. NK-WEB-001; FUN-002/AUT-001..003; UI223/226; SS313;
 * PG-D-115/PT-WEB-142..147.
 */
public final class MenuViewModel {
  private final TopBarViewModel topBar;
  private final List<MenuCard> cards;

  private MenuViewModel(SessionPrincipal principal) {
    topBar = TopBarViewModel.from(principal);
    var selected =
        new ArrayList<>(
            List.of(
                MenuCard.SCENARIOS,
                MenuCard.SEARCH,
                MenuCard.ANIMATION,
                MenuCard.MUSIC,
                MenuCard.QUESTION_NEW,
                MenuCard.NOTIFICATIONS,
                MenuCard.QUESTIONS));
    if (principal.role() == UserRole.ADMIN) {
      selected.add(MenuCard.LOGS);
      selected.add(MenuCard.USERS);
    }
    cards = List.copyOf(selected);
  }

  public static MenuViewModel from(SessionPrincipal principal) {
    return new MenuViewModel(Objects.requireNonNull(principal, "principal"));
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public List<MenuCard> getCards() {
    return cards;
  }

  @Override
  public String toString() {
    return "MenuViewModel[REDACTED]";
  }
}
