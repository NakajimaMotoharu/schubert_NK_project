package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Display-only projection of validated SCFRSP01. Display paths must never enter file resolvers.
 * NK-WEB-001/FUN004/UI223,234/SS313/PG193/PT-WEB-182..193.
 */
@NullMarked
public final class ScenarioFileListViewModel {
  private static final int MAXIMUM_FILE_RECORDS = 500;

  private final TopBarViewModel topBar;
  private final String game;
  private final String prefix;
  private final String routeName;
  private final List<Card> files;

  private ScenarioFileListViewModel(
      SessionPrincipal principal,
      GameCode game,
      int prefix,
      String routeName,
      List<ScenarioFileRecord> records) {
    topBar = TopBarViewModel.from(principal);
    this.game = game.wireValue();
    this.prefix = String.format(Locale.ROOT, "%02d", prefix);
    this.routeName = routeName;
    files = List.copyOf(records.stream().map(Card::new).toList());
  }

  public static ScenarioFileListViewModel from(
      SessionPrincipal principal,
      GameCode game,
      int prefix,
      String routeName,
      List<ScenarioFileRecord> records) {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(game, "game");
    Objects.requireNonNull(routeName, "routeName");
    var copy = List.copyOf(records);
    if (prefix < 0 || prefix > 99) throw new IllegalArgumentException("invalid route prefix");
    if (copy.size() > MAXIMUM_FILE_RECORDS)
      throw new IllegalArgumentException("invalid file list size");
    return new ScenarioFileListViewModel(principal, game, prefix, routeName, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public String getGame() {
    return game;
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

  public String getUpHref() {
    return "/scenarios/" + game;
  }

  public List<Card> getFiles() {
    return files;
  }

  @Override
  public String toString() {
    return "ScenarioFileListViewModel[REDACTED]";
  }

  public static final class Card {
    private final long id;
    private final String displayTitle;
    private final String displayPath;
    private final String href;
    private final int entryCount;

    private Card(ScenarioFileRecord record) {
      id = record.scriptFileId().value();
      displayTitle = record.displayTitle();
      displayPath = record.displayPath().wireValue();
      entryCount = record.entryCount();
      href = "/scenarios/" + id;
    }

    public long getId() {
      return id;
    }

    public String getDisplayTitle() {
      return displayTitle;
    }

    public String getDisplayPath() {
      return displayPath;
    }

    public int getEntryCount() {
      return entryCount;
    }

    public String getHref() {
      return href;
    }

    @Override
    public String toString() {
      return "ScenarioFileCard[REDACTED]";
    }
  }
}
