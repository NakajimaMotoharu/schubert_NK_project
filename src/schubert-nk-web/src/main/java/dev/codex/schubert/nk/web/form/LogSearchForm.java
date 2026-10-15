package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/** SCR014/FUN008/AUT/UI222,225,235/SS313,352/SSC073/PG214/PT-WEB278..285. */
@NullMarked
public final class LogSearchForm {
  public enum Field {
    FORM,
    Q,
    LOG_TYPE,
    ACTION,
    PATH,
    LEVEL,
    FROM,
    TO,
    PAGE
  }

  public enum Code {
    BINDING,
    CHARACTERS,
    LENGTH,
    VALUE,
    RANGE
  }

  private static final Map<String, Field> FIELDS =
      Map.of(
          "q",
          Field.Q,
          "log_type",
          Field.LOG_TYPE,
          "action",
          Field.ACTION,
          "path",
          Field.PATH,
          "level",
          Field.LEVEL,
          "from",
          Field.FROM,
          "to",
          Field.TO,
          "page",
          Field.PAGE);
  private static final Map<Field, Set<String>> CHOICES =
      Map.of(
          Field.LOG_TYPE,
          Set.of("", "ACTION", "REQUEST", "SECURITY", "MQ", "SYSTEM", "BATCH"),
          Field.LEVEL,
          Set.of("", "INFO", "WARN", "ERROR"));
  private static final Map<Field, Integer> LIMITS =
      Map.of(Field.Q, 256, Field.ACTION, 64, Field.PATH, 256);
  private final Map<Field, String> values;
  private final Map<Field, Code> issues;
  private final int page;
  private final Optional<Instant> fromAt;
  private final Optional<Instant> toAt;

  private LogSearchForm(
      Map<Field, String> values,
      Map<Field, Code> issues,
      int page,
      Optional<Instant> fromAt,
      Optional<Instant> toAt) {
    this.values = Map.copyOf(values);
    this.issues = Map.copyOf(issues);
    this.page = page;
    this.fromAt = fromAt;
    this.toAt = toAt;
  }

  public static LogSearchForm bind(Map<String, List<String>> parameters) {
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
    var from = date(Field.FROM, values, issues);
    var to = date(Field.TO, values, issues);
    if (from.isPresent() && to.isPresent()) {
      var difference = Duration.between(from.orElseThrow(), to.orElseThrow());
      if (difference.isNegative() || difference.compareTo(Duration.ofDays(31)) > 0)
        issues.put(Field.TO, Code.RANGE);
    }
    return new LogSearchForm(values, issues, page, from, to);
  }

  private static Optional<Instant> date(
      Field field, Map<Field, String> values, Map<Field, Code> issues) {
    String value = Objects.requireNonNull(values.get(field), "date");
    if (issues.containsKey(field) || value.isEmpty()) return Optional.empty();
    if (!value.matches(
        "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}(:[0-9]{2}(\\.[0-9]{1,3})?)?")) {
      issues.put(field, Code.VALUE);
      return Optional.empty();
    }
    try {
      var parsed =
          LocalDateTime.parse(
              value, DateTimeFormatter.ISO_LOCAL_DATE_TIME.withResolverStyle(ResolverStyle.STRICT));
      if (parsed.getYear() == 0) throw new DateTimeException("invalid year");
      return Optional.of(parsed.toInstant(ZoneOffset.ofHours(9)));
    } catch (DateTimeException failure) {
      issues.put(field, Code.VALUE);
      return Optional.empty();
    }
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

  public LogSearchRequestData toRequest() {
    if (!isValid()) throw new IllegalStateException("invalid log search form");
    return new LogSearchRequestData(
        optional(Field.Q),
        optional(Field.LOG_TYPE).map(LogType::valueOf),
        optional(Field.ACTION),
        optional(Field.PATH),
        optional(Field.LEVEL).map(LogLevel::valueOf),
        fromAt,
        toAt,
        page,
        100);
  }

  private Optional<String> optional(Field field) {
    String value = Objects.requireNonNull(values.get(field), "field");
    return value.isEmpty() ? Optional.empty() : Optional.of(value);
  }

  @Override
  public String toString() {
    return "LogSearchForm[REDACTED]";
  }
}
