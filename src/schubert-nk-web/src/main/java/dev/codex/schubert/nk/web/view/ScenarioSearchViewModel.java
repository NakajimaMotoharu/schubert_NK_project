package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.*;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm.*;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/** Closed SCR003 display state. FUN003/UI222,223,234/SS313,323/PG200/PT-WEB222..229. */
@NullMarked
public final class ScenarioSearchViewModel {
  private final TopBarViewModel topBar;
  private final Filters filters;
  private final List<String> games, speakers;
  private final List<FieldError> errors;
  private final Optional<ScenarioSearchResultsViewModel> results;
  private final Optional<String> previousHref, nextHref;

  private ScenarioSearchViewModel(
      SessionPrincipal actor,
      ScenarioSearchForm form,
      List<String> games,
      List<String> speakers,
      Optional<ScenarioSearchResultsViewModel> results) {
    topBar = TopBarViewModel.from(actor);
    filters = new Filters(form);
    this.games = List.copyOf(games);
    this.speakers = List.copyOf(speakers);
    errors =
        List.copyOf(
            Arrays.stream(Field.values())
                .filter(field -> form.getIssues().containsKey(field))
                .map(
                    field ->
                        new FieldError(field, Objects.requireNonNull(form.getIssues().get(field))))
                .toList());
    this.results = results;
    previousHref = results.flatMap(value -> pageLink(value.getPage().getPreviousPage()));
    nextHref = results.flatMap(value -> pageLink(value.getPage().getNextPage()));
  }

  public static ScenarioSearchViewModel success(
      SessionPrincipal actor,
      ScenarioSearchForm form,
      List<GameRecord> games,
      List<SpeakerRecord> speakers,
      PagedResponseData data,
      List<ScenarioSearchRecord> records) {
    Objects.requireNonNull(form, "form");
    if (!form.isValid()) throw new IllegalArgumentException("invalid successful search form");
    var gameCopy = List.copyOf(games);
    var speakerCopy = List.copyOf(speakers);
    if (gameCopy.size() > 10 || speakerCopy.size() > 500)
      throw new IllegalArgumentException("invalid search candidate count");
    var result = ScenarioSearchResultsViewModel.from(actor, data, records);
    if (result.getPage().getEffectivePage()
        != Math.min(form.getPage(), result.getPage().getTotalPages()))
      throw new IllegalArgumentException("search response page does not match request");
    return new ScenarioSearchViewModel(
        actor,
        form,
        gameCopy.stream().map(value -> value.gameCode().wireValue()).toList(),
        speakerCopy.stream().map(SpeakerRecord::speakerName).toList(),
        Optional.of(result));
  }

  public static ScenarioSearchViewModel invalid(SessionPrincipal actor, ScenarioSearchForm form) {
    Objects.requireNonNull(form, "form");
    if (form.isValid()) throw new IllegalArgumentException("valid form used as invalid");
    return new ScenarioSearchViewModel(
        actor,
        form,
        single(Objects.requireNonNull(form.getValues().get(Field.GAME))),
        single(Objects.requireNonNull(form.getValues().get(Field.SPEAKER))),
        Optional.empty());
  }

  private static List<String> single(String value) {
    return value.isEmpty() ? List.of() : List.of(value);
  }

  private Optional<String> pageLink(OptionalInt page) {
    if (page.isEmpty()) return Optional.empty();
    return Optional.of(
        "/search?q="
            + encode(filters.q)
            + "&game="
            + encode(filters.game)
            + "&speaker="
            + encode(filters.speaker)
            + "&chapter="
            + encode(filters.chapter)
            + "&entry_type="
            + encode(filters.entryType)
            + "&voice="
            + encode(filters.voice)
            + "&page="
            + page.getAsInt());
  }

  private static String encode(String value) {
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Filters getFilters() {
    return filters;
  }

  public List<String> getGames() {
    return games;
  }

  public List<String> getSpeakers() {
    return speakers;
  }

  public List<FieldError> getErrors() {
    return errors;
  }

  public Optional<ScenarioSearchResultsViewModel> getResults() {
    return results;
  }

  public Optional<String> getPreviousHref() {
    return previousHref;
  }

  public Optional<String> getNextHref() {
    return nextHref;
  }

  @Override
  public String toString() {
    return "ScenarioSearchViewModel[REDACTED]";
  }

  public static final class Filters {
    private final String q, game, speaker, chapter, entryType, voice;

    private Filters(ScenarioSearchForm form) {
      var values = form.getValues();
      q = Objects.requireNonNull(values.get(Field.Q));
      game = Objects.requireNonNull(values.get(Field.GAME));
      speaker = Objects.requireNonNull(values.get(Field.SPEAKER));
      chapter = Objects.requireNonNull(values.get(Field.CHAPTER));
      entryType = Objects.requireNonNull(values.get(Field.ENTRY_TYPE));
      voice = Objects.requireNonNull(values.get(Field.VOICE));
    }

    public String getQ() {
      return q;
    }

    public String getGame() {
      return game;
    }

    public String getSpeaker() {
      return speaker;
    }

    public String getChapter() {
      return chapter;
    }

    public String getEntryType() {
      return entryType;
    }

    public String getVoice() {
      return voice;
    }

    @Override
    public String toString() {
      return "SearchFilters[REDACTED]";
    }
  }

  public static final class FieldError {
    private static final Map<Field, String> NAMES =
        Map.of(
            Field.FORM,
            "form",
            Field.Q,
            "q",
            Field.GAME,
            "game",
            Field.SPEAKER,
            "speaker",
            Field.CHAPTER,
            "chapter",
            Field.ENTRY_TYPE,
            "entry_type",
            Field.VOICE,
            "voice",
            Field.PAGE,
            "page");
    private static final Map<Code, String> MESSAGES =
        Map.of(
            Code.BINDING, "入力項目を確認してください。",
            Code.CHARACTERS, "使用できない文字が含まれています。",
            Code.VALUE, "入力値を確認してください。");
    private static final Map<Field, String> LENGTHS =
        Map.of(
            Field.Q, "本文はUTF-8で256 byte以内にしてください。",
            Field.SPEAKER, "話者はUTF-8で128 byte以内にしてください。",
            Field.CHAPTER, "章タイトルはUTF-8で256 byte以内にしてください。");
    private final String name, message;

    private FieldError(Field field, Code code) {
      name = Objects.requireNonNull(NAMES.get(field));
      message =
          Objects.requireNonNull(code == Code.LENGTH ? LENGTHS.get(field) : MESSAGES.get(code));
    }

    public String getName() {
      return name;
    }

    public String getMessage() {
      return message;
    }

    @Override
    public String toString() {
      return "SearchFieldError[REDACTED]";
    }
  }
}
