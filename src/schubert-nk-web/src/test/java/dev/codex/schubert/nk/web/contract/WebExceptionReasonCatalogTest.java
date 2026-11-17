package dev.codex.schubert.nk.web.contract;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.logging.WebLogPayloadException;
import dev.codex.schubert.nk.web.media.MediaDeliveryException;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.messaging.ScenarioWireException;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadException;
import dev.codex.schubert.nk.web.security.MqLoginExchangeException;
import dev.codex.schubert.nk.web.session.SessionPayloadException;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-WEB-REASONRAW001..007; SS311314324333352354/YKT2645; typed public values only. */
final class WebExceptionReasonCatalogTest {
  private static final String UNAVAILABLE = "UNAVAILABLE";

  @Test
  void reasonraw001ScenarioCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        ScenarioWireException.Reason::values,
        ScenarioWireException.Reason::valueOf,
        "INVALID_INPUT",
        "INVALID_RESPONSE",
        UNAVAILABLE);
  }

  @Test
  void reasonraw002ProtectedReadCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        ProtectedReadWireException.Reason::values,
        ProtectedReadWireException.Reason::valueOf,
        "INVALID_INPUT",
        "INVALID_RESPONSE",
        UNAVAILABLE);
  }

  @Test
  void reasonraw003RevocationCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        RevocationPayloadException.Reason::values,
        RevocationPayloadException.Reason::valueOf,
        "PAYLOAD_INVALID",
        "KEY_UNAVAILABLE",
        "CRYPTO_UNAVAILABLE");
  }

  @Test
  void reasonraw004LogCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        WebLogPayloadException.Reason::values,
        WebLogPayloadException.Reason::valueOf,
        "KEY_UNAVAILABLE",
        "PAYLOAD_INVALID",
        "CRYPTO_UNAVAILABLE");
  }

  @Test
  void reasonraw005SessionCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        SessionPayloadException.Reason::values,
        SessionPayloadException.Reason::valueOf,
        "PAYLOAD_INVALID",
        "KEY_UNAVAILABLE",
        "CRYPTO_UNAVAILABLE");
  }

  @Test
  void reasonraw006MediaCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        MediaDeliveryException.Reason::values,
        MediaDeliveryException.Reason::valueOf,
        "INVALID_DESCRIPTOR",
        "BUSY",
        UNAVAILABLE);
  }

  @Test
  void reasonraw007LoginCatalogHasIndependentNamesAndDefensiveArrays() {
    verify(
        MqLoginExchangeException.Reason::values,
        MqLoginExchangeException.Reason::valueOf,
        "INVALID_INPUT",
        UNAVAILABLE);
  }

  private static <E extends Enum<E>> void verify(
      Supplier<E[]> values, Function<String, E> lookup, String... expectedNames) {
    var actual = values.get();
    assertEquals(expectedNames.length, actual.length);
    assertArrayEquals(expectedNames, Arrays.stream(actual).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < expectedNames.length; index++) {
      assertEquals(index, actual[index].ordinal());
      assertSame(actual[index], lookup.apply(expectedNames[index]));
    }
    E first = actual[0];
    actual[0] = actual[actual.length - 1];
    assertSame(first, values.get()[0]);
    assertNotSame(actual, values.get());
    for (String unknown :
        List.of("", "UNKNOWN", expectedNames[0].toLowerCase(Locale.ROOT), expectedNames[0] + " "))
      assertThrows(IllegalArgumentException.class, () -> lookup.apply(unknown));
    assertThrows(NullPointerException.class, () -> lookup.apply(null));
  }
}
