package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.scenario.GameRecord;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Display-only projection of previously validated GAMRSP01;
 * NK-WEB-001/FUN004/UI223,234/SS313/PG193/PT-WEB-182..193.
 */
@NullMarked
public final class GameListViewModel {
  private static final int MAXIMUM_GAME_RECORDS = 10;

  private final TopBarViewModel topBar;
  private final List<Card> games;

  private GameListViewModel(SessionPrincipal principal, List<GameRecord> records) {
    topBar = TopBarViewModel.from(principal);
    games = List.copyOf(records.stream().map(Card::new).toList());
  }

  public static GameListViewModel from(SessionPrincipal principal, List<GameRecord> records) {
    Objects.requireNonNull(principal, "principal");
    var copy = List.copyOf(records);
    if (copy.size() > MAXIMUM_GAME_RECORDS)
      throw new IllegalArgumentException("invalid game list size");
    return new GameListViewModel(principal, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public List<Card> getGames() {
    return games;
  }

  @Override
  public String toString() {
    return "GameListViewModel[REDACTED]";
  }

  public static final class Card {
    private final String code;
    private final String title;
    private final String href;

    private Card(GameRecord record) {
      code = record.gameCode().wireValue();
      title = record.title();
      href = "/scenarios/" + code;
    }

    public String getCode() {
      return code;
    }

    public String getTitle() {
      return title;
    }

    public String getHref() {
      return href;
    }

    @Override
    public String toString() {
      return "GameCard[REDACTED]";
    }
  }
}
