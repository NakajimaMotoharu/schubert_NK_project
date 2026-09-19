package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.scenario.*;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Display-only verified scenario projection. FUN004/UI223,234/SS313,333/PG195/PT-WEB194..205. */
@NullMarked
public final class ScenarioDetailViewModel {
  private final TopBarViewModel topBar;
  private final long id;
  private final String game, title, displayPath;
  private final Optional<Navigation> previous, next;
  private final List<Entry> entries;

  private ScenarioDetailViewModel(
      SessionPrincipal actor, ScenarioDetailResponseData data, List<ScenarioEntryRecord> records) {
    topBar = TopBarViewModel.from(actor);
    id = data.scriptFileId().value();
    game = data.gameCode().wireValue();
    title = data.displayTitle();
    displayPath = data.displayPath().wireValue();
    previous =
        data.previousFileId()
            .map(value -> new Navigation(value.value(), data.previousTitle().orElseThrow()));
    next =
        data.nextFileId()
            .map(value -> new Navigation(value.value(), data.nextTitle().orElseThrow()));
    var projected = new ArrayList<Entry>();
    int start = 0;
    while (start < records.size()) {
      int end = start + 1;
      var first = records.get(start);
      while (end < records.size() && records.get(end).entryId().equals(first.entryId())) {
        var other = records.get(end);
        if (other.lineNumber() != first.lineNumber()
            || other.entryType() != first.entryType()
            || !other.speakerName().equals(first.speakerName())) {
          throw new IllegalArgumentException("inconsistent entry metadata");
        }
        end++;
      }
      projected.add(new Entry(first, records.subList(start, end)));
      start = end;
    }
    entries = List.copyOf(projected);
  }

  public static ScenarioDetailViewModel from(
      SessionPrincipal actor, ScenarioDetailResponseData data, List<ScenarioEntryRecord> records) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(data, "data");
    var copy = List.copyOf(records);
    if (data.previousFileId().isPresent() != data.previousTitle().isPresent()
        || data.nextFileId().isPresent() != data.nextTitle().isPresent()) {
      throw new IllegalArgumentException("inconsistent navigation");
    }
    if (data.deliveryMode() == DeliveryMode.INLINE) {
      if (copy.size() > 200) throw new IllegalArgumentException("invalid inline count");
    } else {
      if (copy.isEmpty() || copy.size() > 10000 || copy.size() != data.fileRecordCount()) {
        throw new IllegalArgumentException("invalid resolved file count");
      }
    }
    PayloadSemanticValidator.validateScenarioSequence(
        copy.stream().map(ScenarioEntryRecord::fields).toList());
    return new ScenarioDetailViewModel(actor, data, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public long getId() {
    return id;
  }

  public String getGame() {
    return game;
  }

  public String getTitle() {
    return title;
  }

  public String getDisplayPath() {
    return displayPath;
  }

  public Optional<Navigation> getPrevious() {
    return previous;
  }

  public Optional<Navigation> getNext() {
    return next;
  }

  public List<Entry> getEntries() {
    return entries;
  }

  @Override
  public String toString() {
    return "ScenarioDetailViewModel[REDACTED]";
  }

  public static final class Navigation {
    private final long id;
    private final String title;

    private Navigation(long id, String title) {
      this.id = id;
      this.title = title;
    }

    public long getId() {
      return id;
    }

    public String getTitle() {
      return title;
    }

    public String getHref() {
      return "/scenarios/" + id;
    }

    @Override
    public String toString() {
      return "ScenarioNavigation[REDACTED]";
    }
  }

  public static final class Entry {
    private final long id;
    private final int sequence, lineNumber;
    private final boolean dialogue;
    private final String speaker, body;
    private final List<Audio> audio;

    private Entry(ScenarioEntryRecord first, List<ScenarioEntryRecord> records) {
      id = first.entryId().value();
      sequence = first.entrySequence();
      lineNumber = first.lineNumber();
      dialogue = first.entryType() == EntryType.DIALOGUE;
      speaker = first.speakerName().orElse("");
      body = first.bodyText();
      var voices = new ArrayList<Audio>();
      for (var record : records) {
        record
            .audioId()
            .ifPresent(
                value ->
                    voices.add(
                        new Audio(
                            value.value(),
                            record.audioSequence(),
                            record.audioDisplayPath().orElseThrow().wireValue())));
      }
      audio = List.copyOf(voices);
    }

    public long getId() {
      return id;
    }

    public int getSequence() {
      return sequence;
    }

    public int getLineNumber() {
      return lineNumber;
    }

    public boolean isDialogue() {
      return dialogue;
    }

    public String getSpeaker() {
      return speaker;
    }

    public String getBody() {
      return body;
    }

    public String getAnchor() {
      return "entry-" + id;
    }

    public List<Audio> getAudio() {
      return audio;
    }

    @Override
    public String toString() {
      return "ScenarioEntry[REDACTED]";
    }
  }

  public static final class Audio {
    private final long id;
    private final int sequence;
    private final String displayPath;

    private Audio(long id, int sequence, String displayPath) {
      this.id = id;
      this.sequence = sequence;
      this.displayPath = displayPath;
    }

    public long getId() {
      return id;
    }

    public int getSequence() {
      return sequence;
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
      return "ScenarioAudio[REDACTED]";
    }
  }
}
