package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** PT-WEB-NFORM001 through NFORM007. No MVC, broker, or database. */
final class NotificationSearchFormTest {
  private static final String TYPE = "type";
  private static final String ACCEPTED_LABEL = "ACCEPTED";
  private static final String ERROR_LABEL = "ERROR";
  private static final String PAGE = "page";
  private static final String FROM = "from";
  private static final String TO = "to";

  @Test
  void nform001DefaultPageAndTheThreeLiteralNotificationTypes() {
    for (var input : List.of(Map.<String, List<String>>of(), Map.of(TYPE, List.of("")))) {
      var form = NotificationSearchForm.bind(input);
      assertEquals(Map.of(), form.getIssues());
      var request = form.toRequest();
      assertEquals(Optional.empty(), request.notificationType());
      assertEquals(Optional.empty(), request.submittedFrom());
      assertEquals(Optional.empty(), request.submittedTo());
      assertEquals(1, form.getPage());
      assertEquals(1, request.page());
      assertEquals(50, request.pageSize());
    }
    Map<String, NotificationType> known =
        Map.of(
            ACCEPTED_LABEL,
            NotificationType.ACCEPTED,
            "COMPLETED",
            NotificationType.COMPLETED,
            ERROR_LABEL,
            NotificationType.ERROR);
    known.forEach(
        (name, expected) ->
            assertEquals(
                Optional.of(expected),
                NotificationSearchForm.bind(Map.of(TYPE, List.of(name)))
                    .toRequest()
                    .notificationType()));
  }

  @Test
  void nform002NoOwnerFieldAndNoAmbiguousOrUnknownType() {
    invalid(Map.of("username", List.of("some-reader")), "form");
    invalid(Map.of("owner", List.of("some-reader")), "form");
    invalid(Map.of(TYPE, List.of()), TYPE);
    invalid(Map.of(TYPE, List.of(ACCEPTED_LABEL, ERROR_LABEL)), TYPE);
    invalid(Map.of(TYPE, List.of("RECEIVED")), TYPE);
  }

  @Test
  void nform003PageMustFitTheDecimalWireField() {
    var last = NotificationSearchForm.bind(Map.of(PAGE, List.of("999999")));
    assertEquals(999_999, last.getPage());
    assertEquals(999_999, last.toRequest().page());
    for (String page : List.of("1000000", "2147483648", "+1", "1.25", "1e3", "２")) {
      invalid(Map.of(PAGE, List.of(page)), PAGE);
    }
  }

  @Test
  void nform004ThirtyFirstDecemberRemainsInsideTheLeapYearRange() {
    var full =
        NotificationSearchForm.bind(Map.of(FROM, List.of("2020-01-01"), TO, List.of("2020-12-31")))
            .toRequest();
    assertEquals(Optional.of(Instant.parse("2019-12-31T15:00:00Z")), full.submittedFrom());
    assertEquals(Optional.of(Instant.parse("2020-12-31T14:59:59.999Z")), full.submittedTo());
    var from = NotificationSearchForm.bind(Map.of(FROM, List.of("2020-02-29"))).toRequest();
    assertEquals(Optional.of(Instant.parse("2020-02-28T15:00:00Z")), from.submittedFrom());
    assertEquals(Optional.empty(), from.submittedTo());
    var to = NotificationSearchForm.bind(Map.of(TO, List.of("2020-02-29"))).toRequest();
    assertEquals(Optional.empty(), to.submittedFrom());
    assertEquals(Optional.of(Instant.parse("2020-02-29T14:59:59.999Z")), to.submittedTo());
    invalid(Map.of(FROM, List.of("2020-01-01"), TO, List.of("2021-01-01")), TO);
    invalid(Map.of(FROM, List.of("2020-06-10"), TO, List.of("2020-06-09")), TO);
  }

  @Test
  void nform005DatesRequireStrictCalendarValuesAndSingleInput() {
    for (String date : List.of("2019-02-29", "2020-02-30", "0000-01-01", "2020/02/29")) {
      invalid(Map.of(FROM, List.of(date)), FROM);
      invalid(Map.of(TO, List.of(date)), TO);
    }
    invalid(Map.of(TO, List.of("2020-02-28", "2020-02-29")), TO);
  }

  @Test
  void nform006ControlSurrogatesAndOutsideEnumDoNotReachTheTypedRequest() {
    for (String tail :
        List.of("\n", "\r", "\t", "\0", String.valueOf(Character.MIN_HIGH_SURROGATE), "😀")) {
      invalid(Map.of(TYPE, List.of(ACCEPTED_LABEL + tail)), TYPE);
    }
  }

  @Test
  void nform007InputSnapshotsAndNullContractsRemainExplicit() {
    var input = new ArrayList<>(List.of("COMPLETED"));
    Map<String, List<String>> parameters = new HashMap<>();
    parameters.put(TYPE, input);
    var form = NotificationSearchForm.bind(parameters);
    input.set(0, ERROR_LABEL);
    parameters.clear();
    assertEquals(Optional.of(NotificationType.COMPLETED), form.toRequest().notificationType());
    assertThrows(
        UnsupportedOperationException.class, () -> form.getValues().put(TYPE, ERROR_LABEL));
    assertThrows(UnsupportedOperationException.class, () -> form.getIssues().put(TYPE, "error"));
    assertFalse(form.toString().contains("COMPLETED"));
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(null));
    parameters.put(null, List.of(ACCEPTED_LABEL));
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(parameters));
    parameters.clear();
    parameters.put(TYPE, null);
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(parameters));
    var nullElement = new ArrayList<String>();
    nullElement.add(null);
    parameters.put(TYPE, nullElement);
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(parameters));
  }

  private static void invalid(Map<String, List<String>> parameters, String field) {
    var form = NotificationSearchForm.bind(parameters);
    assertFalse(form.isValid());
    assertEquals(Set.of(field), form.getIssues().keySet());
    assertThrows(IllegalArgumentException.class, form::toRequest);
  }
}
