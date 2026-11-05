package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Locale;
import org.junit.jupiter.api.Test;

/** WEB-SAVED-PORT-001..008; UI221/226/SS313314352, literal data only, no HTTP/redirect/session. */
final class SavedScreenTargetPortTest {
  private static final String GET = "GET";
  private static final String SEARCH_QUERY = "/search?q=";
  private static final String FIELD_VALUE = "=public-fixture";
  private static final String FIXED_FAILURE = "saved screen target is invalid";

  @Test
  void everyApprovedScreenFamilyRetainsItsIndependentLiteralLocation() {
    for (String location :
        List.of(
            "/",
            "/search",
            "/logs",
            "/scenarios",
            "/scenarios/12",
            "/scenarios/12/34",
            "/animation",
            "/animation/main",
            "/animation/ova",
            "/animation/opening",
            "/animation/videos/12",
            "/music",
            "/music/album",
            "/music/album/track",
            "/music/media2",
            "/music/downloads",
            "/admin/users",
            "/admin/users/12",
            "/questions",
            "/questions/12",
            "/questions/accepted/12",
            "/notifications",
            "/notifications/12")) {
      var target = SavedScreenTarget.fromGet(GET, location);
      assertEquals(location, target.location());
      assertEquals("SavedScreenTarget[REDACTED]", target.toString());
    }
  }

  @Test
  void rawQuerySpellingEmptyFieldsAndBenignValuesRemainUnchangedAndObjectsIndependent() {
    for (String location :
        List.of(
            "/search?",
            "/search?q=two+words",
            "/search?q=%E6%97%A5%E6%9C%AC&x=a%26b",
            "/search?q=password&unrelated=token",
            "/search?x&&empty=&bare",
            "/search?q=first&q=second",
            "/scenarios/%E6%97%A5%E6%9C%AC?category=one;two")) {
      var first = SavedScreenTarget.fromGet(GET, location);
      var second = SavedScreenTarget.fromGet(GET, "/logs?page=2");
      assertEquals(location, first.location());
      assertEquals("/logs?page=2", second.location());
    }
  }

  @Test
  void unsupportedFamiliesReservedMediaAndOverDeepLocationsRejectWithNoValueInFailure() {
    for (String location :
        List.of(
            "/login",
            "/logout",
            "/error",
            "/actuator",
            "/api",
            "/media",
            "/Search",
            "/admin",
            "/admin/Users",
            "/admin/users/1/extra",
            "/scenarios/1/2/3",
            "/animation/unknown",
            "/animation/videos",
            "/animation/videos/1/extra",
            "/music/media",
            "/music/media/item",
            "/music/download",
            "/music/download/item",
            "/music/a/b/c",
            "/questions/1/extra",
            "/notifications/1/extra")) {
      rejected(GET, location);
    }
  }

  @Test
  void eachSecretParameterNameRejectsInMixedCasePercentSpellingAndNonFirstPosition() {
    for (String name :
        List.of(
            "password",
            "passwordconfirmation",
            "confirmpassword",
            "_csrf",
            "csrf",
            "csrftoken",
            "operationtoken",
            "authenticationcontext",
            "authenticationcontextid",
            "session",
            "sessionid",
            "token",
            "jsessionid",
            "schubert_nk_session")) {
      rejected(GET, "/search?" + name + FIELD_VALUE);
      rejected(GET, "/search?q=term&" + name.toUpperCase(Locale.ROOT) + FIELD_VALUE);
      String escaped = "%" + Integer.toHexString(name.charAt(0)) + name.substring(1);
      rejected(GET, "/search?" + escaped + FIELD_VALUE);
    }
  }

  @Test
  void rawAndEncodedPathParametersRejectWhileSemicolonsInsideQueryRemainData() {
    for (String location :
        List.of(
            "/scenarios/1;id=public-fixture", "/scenarios/1%3Bid=public-fixture",
            "/scenarios/1%3bid=public-fixture", "/;public")) rejected(GET, location);
    assertEquals("/search?q=a;b", SavedScreenTarget.fromGet(GET, "/search?q=a;b").location());
  }

  @Test
  void underlyingGetRelativeUriDelimiterDotAndFragmentFailuresAreWrappedAsFixedScreenFailure() {
    for (String location :
        List.of(
            "",
            "search",
            "mailto:public",
            "https://public.invalid/search",
            "//public.invalid/search",
            "/../search",
            "/a/../search",
            "/./search",
            "/scenarios//1",
            "/search#fragment",
            "/scenarios/%2e%2e",
            "/scenarios/%2Fname",
            "/scenarios/%5cname",
            "/search?q=%GG",
            "/search?q=has space",
            "/search?q=\u2028",
            "/search?q=\u2029",
            "/search?q=\uD800")) rejected(GET, location);
  }

  @Test
  void explicitNullContractsAndEveryNonGetMethodFailBeforeRetainingALocation() {
    assertThrows(NullPointerException.class, () -> SavedScreenTarget.fromGet(null, "/search"));
    assertThrows(NullPointerException.class, () -> SavedScreenTarget.fromGet(GET, null));
    for (String method : List.of("", "get", "HEAD", "POST", "PUT", "DELETE"))
      rejected(method, "/search");
  }

  @Test
  void exactUtf8TwoThousandFortyEightByteBoundPreservesAsciiAndMultibyteQueries() {
    for (String location :
        List.of(SEARCH_QUERY + "a".repeat(2038), SEARCH_QUERY + "é".repeat(1019))) {
      assertEquals(2048, location.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(location, SavedScreenTarget.fromGet(GET, location).location());
    }
    String excessive = SEARCH_QUERY + "a".repeat(2039);
    assertEquals(2049, excessive.getBytes(StandardCharsets.UTF_8).length);
    rejected(GET, excessive);
  }

  private static void rejected(String method, String location) {
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> SavedScreenTarget.fromGet(method, location));
    assertEquals(FIXED_FAILURE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
