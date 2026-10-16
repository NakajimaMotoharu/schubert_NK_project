package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import java.text.Normalizer;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/** SCR020/NTF/UI224,236/SS313,314; PG-D347/PT-NTF-HTTP001..010. No owner input. */
@NullMarked
public final class NotificationSearchForm {
  private static final java.lang.String LITERAL_TYPE = "type";

  private static final java.lang.String LITERAL_PAGE = "page";

  private static final Set<String> FIELDS = Set.of(LITERAL_TYPE, "from", "to", LITERAL_PAGE);
  private static final String INVALID = "入力項目を確認してください。";
  private final Map<String, String> values;
  private final Map<String, String> issues;
  private final int page;
  private final Optional<Instant> from;
  private final Optional<Instant> to;

  private NotificationSearchForm(
      Map<String, String> values,
      Map<String, String> issues,
      int page,
      Optional<Instant> from,
      Optional<Instant> to) {
    this.values = Map.copyOf(values);
    this.issues = Map.copyOf(issues);
    this.page = page;
    this.from = from;
    this.to = to;
  }

  public static NotificationSearchForm bind(Map<String, List<String>> parameters) {
    Objects.requireNonNull(parameters, "parameters");
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var values = new HashMap<String, String>();
    var issues = new HashMap<String, String>();
    if (!FIELDS.containsAll(snapshot.keySet())) issues.put("form", INVALID);
    for (String name : FIELDS) {
      var input = snapshot.getOrDefault(name, List.of(""));
      String value = "";
      if (input.size() != 1) issues.put(name, INVALID);
      else {
        String raw = input.getFirst();
        if (raw.codePoints().anyMatch(NotificationSearchForm::invalidCharacter))
          issues.put(name, INVALID);
        else value = Normalizer.normalize(raw, Normalizer.Form.NFC).trim();
      }
      values.put(name, value);
    }
    if (!Set.of("", "ACCEPTED", "COMPLETED", "ERROR").contains(values.get(LITERAL_TYPE)))
      issues.put(LITERAL_TYPE, INVALID);
    String text = Objects.requireNonNull(values.get(LITERAL_PAGE));
    int page = 1;
    if (!text.isEmpty()) {
      if (!text.matches("-?[0-9]+")) issues.put(LITERAL_PAGE, INVALID);
      else
        try {
          int number = Integer.parseInt(text);
          if (number > 999999) issues.put(LITERAL_PAGE, INVALID);
          else page = Math.max(1, number);
        } catch (NumberFormatException failure) {
          issues.put(LITERAL_PAGE, INVALID);
        }
    }
    var from = date("from", values, issues);
    var to = date("to", values, issues);
    if (from.isPresent() && to.isPresent()) {
      var difference = Duration.between(from.orElseThrow(), to.orElseThrow());
      if (difference.isNegative() || difference.compareTo(Duration.ofDays(366)) > 0)
        issues.put("to", "受付日は366日以内で指定してください。");
    }
    return new NotificationSearchForm(values, issues, page, from, to);
  }

  private static Optional<Instant> date(
      String name, Map<String, String> values, Map<String, String> issues) {
    String text = Objects.requireNonNull(values.get(name));
    if (issues.containsKey(name) || text.isEmpty()) return Optional.empty();
    if (!text.matches("[0-9]{4}-[0-9]{2}-[0-9]{2}")) {
      issues.put(name, INVALID);
      return Optional.empty();
    }
    try {
      var day =
          LocalDate.parse(
              text, DateTimeFormatter.ISO_LOCAL_DATE.withResolverStyle(ResolverStyle.STRICT));
      if (day.getYear() == 0) throw new DateTimeException("invalid year");
      var time = name.equals("from") ? day.atStartOfDay() : day.atTime(23, 59, 59, 999_000_000);
      return Optional.of(time.toInstant(ZoneOffset.ofHours(9)));
    } catch (DateTimeException failure) {
      issues.put(name, INVALID);
      return Optional.empty();
    }
  }

  private static boolean invalidCharacter(int value) {
    return Character.isISOControl(value)
        || (value >= Character.MIN_SURROGATE && value <= Character.MAX_SURROGATE);
  }

  public boolean isValid() {
    return issues.isEmpty();
  }

  public Map<String, String> getValues() {
    return values;
  }

  public Map<String, String> getIssues() {
    return issues;
  }

  public int getPage() {
    return page;
  }

  public NotificationSearchRequestData toRequest() {
    if (!isValid()) throw new IllegalArgumentException("invalid notification search form");
    String type = Objects.requireNonNull(values.get(LITERAL_TYPE));
    return new NotificationSearchRequestData(
        type.isEmpty() ? Optional.empty() : Optional.of(NotificationType.valueOf(type)),
        from,
        to,
        page,
        50);
  }

  @Override
  public String toString() {
    return "NotificationSearchForm[REDACTED]";
  }
}
