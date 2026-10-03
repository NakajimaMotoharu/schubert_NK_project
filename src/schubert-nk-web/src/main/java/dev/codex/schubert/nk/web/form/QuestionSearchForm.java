package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.*;
import java.time.format.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR022/UI224236/SS313314; PG-D350/PT-QRY-HTTP001..003,012. No HTTP role/context. */
@NullMarked
public final class QuestionSearchForm {
  private static final Set<String> FIELDS =
      Set.of("keyword", "username", "state", "from", "to", "page");
  private static final String INVALID = "入力項目を確認してください。";
  private final Map<String, String> values, issues;
  private final boolean admin;
  private final int page;
  private final Optional<Instant> from, to;

  private QuestionSearchForm(
      Map<String, String> values,
      Map<String, String> issues,
      boolean admin,
      int page,
      Optional<Instant> from,
      Optional<Instant> to) {
    this.values = Map.copyOf(values);
    this.issues = Map.copyOf(issues);
    this.admin = admin;
    this.page = page;
    this.from = from;
    this.to = to;
  }

  public static QuestionSearchForm bind(Map<String, List<String>> parameters, UserRole role) {
    Objects.requireNonNull(parameters, "parameters");
    boolean admin = Objects.requireNonNull(role, "role") == UserRole.ADMIN;
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var values = new HashMap<String, String>();
    var issues = new HashMap<String, String>();
    if (!FIELDS.containsAll(snapshot.keySet())) issues.put("form", INVALID);
    if (!admin && snapshot.containsKey("username")) issues.put("username", INVALID);
    for (String name : FIELDS) {
      var input = snapshot.getOrDefault(name, List.of(""));
      String value = "";
      if (input.size() != 1) issues.put(name, INVALID);
      else {
        String raw = input.getFirst();
        if (raw.codePoints().anyMatch(QuestionSearchForm::invalidCharacter))
          issues.put(name, INVALID);
        else value = Normalizer.normalize(raw, Normalizer.Form.NFC).trim();
      }
      values.put(name, value);
    }
    if (!admin) values.put("username", "");
    if (Objects.requireNonNull(values.get("keyword")).getBytes(StandardCharsets.UTF_8).length > 256)
      issues.put("keyword", INVALID);
    if (Objects.requireNonNull(values.get("username")).getBytes(StandardCharsets.UTF_8).length > 64)
      issues.put("username", INVALID);
    if (!Set.of("", "ANSWERED", "UNANSWERED", "ERROR").contains(values.get("state")))
      issues.put("state", INVALID);
    int page = 1;
    String text = Objects.requireNonNull(values.get("page"));
    if (!text.isEmpty()) {
      if (!text.matches("-?[0-9]+")) issues.put("page", INVALID);
      else
        try {
          int number = Integer.parseInt(text);
          if (number > 999999) issues.put("page", INVALID);
          else page = Math.max(1, number);
        } catch (NumberFormatException failure) {
          issues.put("page", INVALID);
        }
    }
    var from = date("from", values, issues);
    var to = date("to", values, issues);
    if (from.isPresent() && to.isPresent()) {
      var difference = Duration.between(from.orElseThrow(), to.orElseThrow());
      if (difference.isNegative() || difference.compareTo(Duration.ofDays(366)) > 0)
        issues.put("to", "受付日は366日以内で指定してください。");
    }
    return new QuestionSearchForm(values, issues, admin, page, from, to);
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

  public boolean isAdmin() {
    return admin;
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

  public QuestionSearchRequestData toRequest() {
    if (!isValid()) throw new IllegalArgumentException("invalid question search form");
    String keyword = Objects.requireNonNull(values.get("keyword"));
    String username = Objects.requireNonNull(values.get("username"));
    String state = Objects.requireNonNull(values.get("state"));
    return new QuestionSearchRequestData(
        keyword.isEmpty() ? Optional.empty() : Optional.of(keyword),
        username.isEmpty() ? Optional.empty() : Optional.of(username),
        state.isEmpty() ? Optional.empty() : Optional.of(AnswerState.valueOf(state)),
        from,
        to,
        page,
        50);
  }

  @Override
  public String toString() {
    return "QuestionSearchForm[REDACTED]";
  }
}
