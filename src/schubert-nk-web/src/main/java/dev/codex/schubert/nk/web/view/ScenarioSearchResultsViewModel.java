package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Verified search response to display-only values. FUN003/UI223,234/SS313,323/PG198/PT-WEB206..213.
 */
@NullMarked
public final class ScenarioSearchResultsViewModel {
  private final TopBarViewModel topBar;
  private final PageViewModel page;
  private final List<Row> rows;

  private ScenarioSearchResultsViewModel(
      SessionPrincipal actor, PageViewModel page, List<ScenarioSearchRecord> records) {
    topBar = TopBarViewModel.from(actor);
    this.page = page;
    rows = List.copyOf(records.stream().map(Row::new).toList());
  }

  public static ScenarioSearchResultsViewModel from(
      SessionPrincipal actor, PagedResponseData data, List<ScenarioSearchRecord> records) {
    Objects.requireNonNull(actor, "actor");
    var page = PageViewModel.from(data, 100);
    var copy = List.copyOf(records);
    long expected = page.isEmpty() ? 0 : page.getLastResult() - page.getFirstResult() + 1;
    if (copy.size() != expected)
      throw new IllegalArgumentException("inconsistent search record count");
    return new ScenarioSearchResultsViewModel(actor, page, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public PageViewModel getPage() {
    return page;
  }

  public List<Row> getRows() {
    return rows;
  }

  @Override
  public String toString() {
    return "ScenarioSearchResultsViewModel[REDACTED]";
  }

  public static final class Row {
    private final long entryId;
    private final long scriptFileId;
    private final int lineNumber;
    private final String game;
    private final String chapterTitle;
    private final String entryTypeLabel;
    private final String speaker;
    private final String body;
    private final String scriptDisplayPath;
    private final Optional<Audio> audio;

    private Row(ScenarioSearchRecord record) {
      if (record.lineNumber() < 1
          || record.audioPresent() != record.audioId().isPresent()
          || record.audioPresent() != record.audioDisplayPath().isPresent()) {
        throw new IllegalArgumentException("invalid search display record");
      }
      entryId = record.entryId().value();
      scriptFileId = record.scriptFileId().value();
      game = record.gameCode().wireValue();
      chapterTitle = record.chapterTitle().orElse("");
      lineNumber = record.lineNumber();
      entryTypeLabel = record.entryType() == EntryType.DIALOGUE ? "セリフ" : "ナレーション";
      speaker = record.speakerName().orElse("");
      body = record.bodyText();
      scriptDisplayPath = record.scriptDisplayPath().wireValue();
      audio =
          record
              .audioId()
              .map(
                  value ->
                      new Audio(
                          value.value(), record.audioDisplayPath().orElseThrow().wireValue()));
    }

    public long getEntryId() {
      return entryId;
    }

    public long getScriptFileId() {
      return scriptFileId;
    }

    public String getGame() {
      return game;
    }

    public String getChapterTitle() {
      return chapterTitle;
    }

    public int getLineNumber() {
      return lineNumber;
    }

    public String getEntryTypeLabel() {
      return entryTypeLabel;
    }

    public String getSpeaker() {
      return speaker;
    }

    public String getBody() {
      return body;
    }

    public String getScriptDisplayPath() {
      return scriptDisplayPath;
    }

    public String getScenarioHref() {
      return "/scenarios/" + scriptFileId + "#entry-" + entryId;
    }

    public Optional<Audio> getAudio() {
      return audio;
    }

    @Override
    public String toString() {
      return "ScenarioSearchRow[REDACTED]";
    }
  }

  public static final class Audio {
    private final long id;
    private final String displayPath;

    private Audio(long id, String displayPath) {
      this.id = id;
      this.displayPath = displayPath;
    }

    public long getId() {
      return id;
    }

    public String getDisplayPath() {
      return displayPath;
    }

    public String getHref() {
      return "/audio/" + id;
    }

    public String getDownloadHref() {
      return "/audio/" + id + "/download";
    }

    @Override
    public String toString() {
      return "ScenarioSearchAudio[REDACTED]";
    }
  }
}
