package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Labels;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Method;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Metric;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Route;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Status;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** GENWEB001..004/1658: independent public value contracts; no HTTP/DB/runtime actions. */
class GeneratedWebValueContractTest {
  private record Expected<E extends Enum<E>>(String literal, E constant) {}

  private static <E extends Enum<E>> Expected<E> e(String literal, E constant) {
    return new Expected<>(literal, constant);
  }

  private static <E extends Enum<E>> void enumeration(
      Supplier<E[]> values, Function<String, E> lookup, List<Expected<E>> expected) {
    var actual = values.get();
    assertEquals(
        expected.stream().map(Expected::literal).toList(),
        Arrays.stream(actual).map(Enum::name).toList());
    for (var item : expected) assertSame(item.constant(), lookup.apply(item.literal()));
    assertThrows(IllegalArgumentException.class, () -> lookup.apply("UNKNOWN_ENUM"));
    assertThrows(NullPointerException.class, () -> lookup.apply(null));
    actual[0] = expected.getLast().constant();
    assertSame(expected.getFirst().constant(), values.get()[0]);
  }

  @Test
  void genWeb001MetricAndMethodFactoriesHaveExactLiteralContracts() {
    enumeration(
        Metric::values,
        Metric::valueOf,
        List.of(e("REQUESTS", Metric.REQUESTS), e("DURATION", Metric.DURATION)));
    enumeration(
        Method::values,
        Method::valueOf,
        List.of(
            e("GET", Method.GET),
            e("HEAD", Method.HEAD),
            e("POST", Method.POST),
            e("PUT", Method.PUT),
            e("PATCH", Method.PATCH),
            e("DELETE", Method.DELETE),
            e("OPTIONS", Method.OPTIONS),
            e("TRACE", Method.TRACE),
            e("CONNECT", Method.CONNECT),
            e("OTHER", Method.OTHER)));
  }

  @Test
  void genWeb002EveryRouteFactoryIsClosedAndDefensivelyCopied() {
    enumeration(
        Route::values,
        Route::valueOf,
        List.of(
            e("ROOT", Route.ROOT),
            e("LOGIN", Route.LOGIN),
            e("LOGOUT", Route.LOGOUT),
            e("SEARCH", Route.SEARCH),
            e("LOGS", Route.LOGS),
            e("ERROR", Route.ERROR),
            e("SCENARIOS", Route.SCENARIOS),
            e("SCENARIO_ID", Route.SCENARIO_ID),
            e("SCENARIO_GAME", Route.SCENARIO_GAME),
            e("SCENARIO_PREFIX", Route.SCENARIO_PREFIX),
            e("ANIMATION", Route.ANIMATION),
            e("ANIMATION_MAIN", Route.ANIMATION_MAIN),
            e("ANIMATION_OVA", Route.ANIMATION_OVA),
            e("ANIMATION_OPENING", Route.ANIMATION_OPENING),
            e("ANIMATION_VIDEO", Route.ANIMATION_VIDEO),
            e("ANIMATION_MEDIA", Route.ANIMATION_MEDIA),
            e("MUSIC", Route.MUSIC),
            e("MUSIC_CATEGORY", Route.MUSIC_CATEGORY),
            e("MUSIC_SECTION", Route.MUSIC_SECTION),
            e("MUSIC_MEDIA", Route.MUSIC_MEDIA),
            e("MUSIC_DOWNLOAD", Route.MUSIC_DOWNLOAD),
            e("AUDIO", Route.AUDIO),
            e("AUDIO_DOWNLOAD", Route.AUDIO_DOWNLOAD),
            e("ADMIN_USERS", Route.ADMIN_USERS),
            e("ADMIN_USER_NEW", Route.ADMIN_USER_NEW),
            e("ADMIN_USER_ID", Route.ADMIN_USER_ID),
            e("QUESTIONS", Route.QUESTIONS),
            e("QUESTION_NEW", Route.QUESTION_NEW),
            e("QUESTION_ACCEPTED", Route.QUESTION_ACCEPTED),
            e("QUESTION_ID", Route.QUESTION_ID),
            e("NOTIFICATIONS", Route.NOTIFICATIONS),
            e("NOTIFICATION_ID", Route.NOTIFICATION_ID),
            e("STYLES", Route.STYLES),
            e("SCRIPTS", Route.SCRIPTS),
            e("UNKNOWN", Route.UNKNOWN)));
  }

  @Test
  void genWeb003StatusFactoriesUseAllFiveLiteralConstants() {
    enumeration(
        Status::values,
        Status::valueOf,
        List.of(
            e("INFORMATIONAL", Status.INFORMATIONAL),
            e("SUCCESS", Status.SUCCESS),
            e("REDIRECTION", Status.REDIRECTION),
            e("CLIENT_ERROR", Status.CLIENT_ERROR),
            e("SERVER_ERROR", Status.SERVER_ERROR)));
  }

  @Test
  void genWeb004LabelValueContractsUseEveryComponentAndPlatformHash() {
    var actual = new Labels(Route.LOGIN, Method.POST, Status.SUCCESS);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not labels";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(new Labels(Route.LOGIN, Method.POST, Status.SUCCESS)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    for (var changed :
        List.of(
            new Labels(Route.ROOT, Method.POST, Status.SUCCESS),
            new Labels(Route.LOGIN, Method.GET, Status.SUCCESS),
            new Labels(Route.LOGIN, Method.POST, Status.SERVER_ERROR)))
      assertFalse(actual.equals(changed));
    // Enum.hashCode is final platform identity; expected never calls Labels.hashCode.
    int expected =
        31 * (31 * System.identityHashCode(Route.LOGIN) + System.identityHashCode(Method.POST))
            + System.identityHashCode(Status.SUCCESS);
    assertEquals(expected, actual.hashCode());
    assertEquals("Labels[route=LOGIN, method=POST, status=SUCCESS]", actual.toString());
    assertSame(Route.LOGIN, actual.route());
    assertSame(Method.POST, actual.method());
    assertSame(Status.SUCCESS, actual.status());
  }
}
