package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.scenario.RouteRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Display-only projection of validated RTERSP01; caller owns game binding.
 * NK-WEB-001/FUN004/UI223,234/SS313/PG193/PT-WEB-182..193.
 */
@NullMarked
public final class RouteListViewModel {
  private static final int MAXIMUM_ROUTE_RECORDS = 50;

  private final TopBarViewModel topBar;
  private final String game;
  private final List<Card> routes;

  private RouteListViewModel(SessionPrincipal principal, GameCode game, List<RouteRecord> records) {
    topBar = TopBarViewModel.from(principal);
    this.game = game.wireValue();
    routes = List.copyOf(records.stream().map(record -> new Card(this.game, record)).toList());
  }

  public static RouteListViewModel from(
      SessionPrincipal principal, GameCode game, List<RouteRecord> records) {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(game, "game");
    var copy = List.copyOf(records);
    if (copy.size() > MAXIMUM_ROUTE_RECORDS)
      throw new IllegalArgumentException("invalid route list size");
    return new RouteListViewModel(principal, game, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public String getGame() {
    return game;
  }

  public String getUpHref() {
    return "/scenarios";
  }

  public List<Card> getRoutes() {
    return routes;
  }

  @Override
  public String toString() {
    return "RouteListViewModel[REDACTED]";
  }

  public static final class Card {
    private final String prefix;
    private final String routeName;
    private final String href;
    private final int fileCount;

    private Card(String game, RouteRecord record) {
      prefix = String.format(Locale.ROOT, "%02d", record.prefix());
      routeName = record.routeName();
      fileCount = record.fileCount();
      href = "/scenarios/" + game + "/" + prefix;
    }

    public String getPrefix() {
      return prefix;
    }

    public String getRouteName() {
      return routeName;
    }

    public String getTitle() {
      return prefix + ": " + routeName;
    }

    public int getFileCount() {
      return fileCount;
    }

    public String getHref() {
      return href;
    }

    @Override
    public String toString() {
      return "RouteCard[REDACTED]";
    }
  }
}
