package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Search input boundary. FUN003/UI222,223,234/SS313,352/SSC072/PG199/PT-WEB214..221. */
@NullMarked
public final class ScenarioSearchForm {
  public enum Field {
    FORM,
    Q,
    GAME,
    SPEAKER,
    CHAPTER,
    ENTRY_TYPE,
    VOICE,
    PAGE
  }

  public enum Code {
    BINDING,
    CHARACTERS,
    LENGTH,
    VALUE
  }

  private static final Map<String, Field> FIELDS =
      Map.of(
          "q",
          Field.Q,
          "game",
          Field.GAME,
          "speaker",
          Field.SPEAKER,
          "chapter",
          Field.CHAPTER,
          "entry_type",
          Field.ENTRY_TYPE,
          "voice",
          Field.VOICE,
          "page",
          Field.PAGE);
  private static final Map<Field, Set<String>> CHOICES =
      Map.of(
          Field.GAME, Set.of("", "NUKITASHI1", "NUKITASHI2"),
          Field.ENTRY_TYPE, Set.of("", "dialogue", "narration"),
          Field.VOICE, Set.of("", "with", "without"));
  private static final Map<Field, Integer> LIMITS =
      Map.of(Field.Q, 256, Field.SPEAKER, 128, Field.CHAPTER, 256);
  private final Map<Field, String> values;
  private final Map<Field, Code> issues;
  private final int page;

  private ScenarioSearchForm(Map<Field, String> values, Map<Field, Code> issues, int page) {
    this.values = Map.copyOf(values);
    this.issues = Map.copyOf(issues);
    this.page = page;
  }

  public static ScenarioSearchForm bind(Map<String, List<String>> parameters) {
    Objects.requireNonNull(parameters, "parameters");
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var values = new EnumMap<Field, String>(Field.class);
    var issues = new EnumMap<Field, Code>(Field.class);
    if (!FIELDS.keySet().containsAll(snapshot.keySet())) issues.put(Field.FORM, Code.BINDING);
    FIELDS.forEach(
        (name, field) -> {
          var input = snapshot.getOrDefault(name, List.of(""));
          if (input.size() != 1) {
            values.put(field, "");
            issues.put(field, Code.BINDING);
          } else {
            String raw = input.getFirst();
            if (invalidCharacters(raw)) {
              values.put(field, "");
              issues.put(field, Code.CHARACTERS);
            } else {
              String normalized = Normalizer.normalize(raw, Normalizer.Form.NFC).trim();
              values.put(field, normalized);
              int maximum = LIMITS.getOrDefault(field, Integer.MAX_VALUE);
              if (normalized.getBytes(StandardCharsets.UTF_8).length > maximum)
                issues.put(field, Code.LENGTH);
            }
          }
        });
    CHOICES.forEach(
        (field, allowed) -> {
          if (!allowed.contains(Objects.requireNonNull(values.get(field), "field")))
            issues.putIfAbsent(field, Code.VALUE);
        });
    int page = 1;
    String text = Objects.requireNonNull(values.get(Field.PAGE), "page");
    if (!text.isEmpty()) {
      if (!text.matches("-?[0-9]+")) issues.putIfAbsent(Field.PAGE, Code.VALUE);
      else {
        try {
          int parsed = Integer.parseInt(text);
          if (parsed > 999999) issues.putIfAbsent(Field.PAGE, Code.VALUE);
          else page = Math.max(1, parsed);
        } catch (NumberFormatException exception) {
          issues.putIfAbsent(Field.PAGE, Code.VALUE);
        }
      }
    }
    return new ScenarioSearchForm(values, issues, page);
  }

  private static boolean invalidCharacters(String value) {
    for (int i = 0; i < value.length(); i++) {
      char c = value.charAt(i);
      if (c == '\r' || c == '\n' || c == '\t' || c == 0) return true;
      if (Character.isHighSurrogate(c)) {
        if (i + 1 == value.length() || !Character.isLowSurrogate(value.charAt(i + 1))) return true;
        i++;
      } else if (Character.isLowSurrogate(c)) return true;
    }
    return false;
  }

  public Map<Field, Code> getIssues() {
    return issues;
  }

  public Map<Field, String> getValues() {
    return values;
  }

  public boolean isValid() {
    return issues.isEmpty();
  }

  public int getPage() {
    return page;
  }

  public ScenarioSearchRequestData toRequest() {
    if (!isValid()) throw new IllegalStateException("invalid search form");
    return new ScenarioSearchRequestData(
        optional(Field.Q),
        optional(Field.GAME)
            .map(value -> value.equals("NUKITASHI1") ? GameCode.NUKITASHI_1 : GameCode.NUKITASHI_2),
        optional(Field.SPEAKER),
        optional(Field.CHAPTER),
        optional(Field.ENTRY_TYPE).map(value -> EntryType.valueOf(value.toUpperCase(Locale.ROOT))),
        optional(Field.VOICE)
            .map(value -> value.equals("with") ? VoiceCondition.PRESENT : VoiceCondition.ABSENT),
        page,
        100);
  }

  private Optional<String> optional(Field field) {
    String value = Objects.requireNonNull(values.get(field), "field");
    return value.isEmpty() ? Optional.empty() : Optional.of(value);
  }

  @Override
  public String toString() {
    return "ScenarioSearchForm[REDACTED]";
  }
}
