package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/**
 * PT-OPS-API-CONFIG-SSC301001..008; SYS002/004, UI243/253, SS342/343 SSC301. No OS admission,
 * credentials, DB/JMS, native readiness or actual API success is claimed.
 */
final class ApiAdmittedConfigurationTest {
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  private static final Map<String, String> ENV =
      Map.of(
          "SCHUBERT_NK_CONFIG_DIR",
          "/etc/schubert-nk",
          "CREDENTIALS_DIRECTORY",
          "/run/credentials/service");

  private static ApiStartupInputs.Values values() throws Exception {
    return new ApiStartupInputs(service -> new ServiceConfigFiles.Contents("", ""), ENV).load();
  }

  @Test
  void ssc301001SameValuesAndIndependentCanonicalGolden() throws Exception {
    var input = values();
    int[] status = {50};
    var calls = new AtomicInteger();
    var result =
        ApiProcessMain.admittedConfiguration(
            () -> {
              calls.incrementAndGet();
              return input;
            },
            status);
    assertSame(input, result.value());
    // Independent SS343/default key=value LF golden from ApiNonSecretConfigTest,
    // hashed with Python hashlib, not a Production canonical/hash method.
    assertEquals(
        "afec3045ebed78de9d1fab75daf34d7ca4e2bd990b110f3c6afac97def435796", result.sha256());
    assertEquals(50, status[0]);
    assertEquals(1, calls.get());
  }

  @Test
  void ssc301002RealMalformedLoaderMapsOnlyToFixed70() {
    var calls = new AtomicInteger();
    var loader =
        new ApiStartupInputs(
            service -> {
              calls.incrementAndGet();
              assertEquals(ServiceConfigFiles.Service.API, service);
              return new ServiceConfigFiles.Contents("", "nk.protocol.version: INVALID\n");
            },
            ENV);
    int[] status = {50};
    var failure =
        assertThrows(
            IOException.class, () -> ApiProcessMain.admittedConfiguration(loader::load, status));
    assertEquals(70, status[0]);
    assertEquals("non-secret configuration unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(1, calls.get());
  }

  @Test
  void ssc301003AlgorithmFailureHasNoUntrustedCause() {
    int[] status = {50};
    var failure =
        assertThrows(
            IOException.class,
            () ->
                ApiProcessMain.admittedConfiguration(
                    () -> {
                      throw new NoSuchAlgorithmException(FIXTURE_UNTRUSTED_6FC6869D);
                    },
                    status));
    assertEquals(70, status[0]);
    assertEquals("non-secret configuration unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void ssc301004IoFailureIdentityAnd50Remain() {
    int[] status = {50};
    var original = new IOException(FIXTURE_UNTRUSTED_6FC6869D);
    assertSame(
        original,
        assertThrows(
            IOException.class,
            () ->
                ApiProcessMain.admittedConfiguration(
                    () -> {
                      throw original;
                    },
                    status)));
    assertEquals(50, status[0]);
  }

  @Test
  void ssc301005UnknownRuntimeAndErrorRemainUnknown() {
    int[] status = {50};
    var runtime = new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                ApiProcessMain.admittedConfiguration(
                    () -> {
                      throw runtime;
                    },
                    status)));
    var fatal = new AssertionError(FIXTURE_UNTRUSTED_6FC6869D);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                ApiProcessMain.admittedConfiguration(
                    () -> {
                      throw fatal;
                    },
                    status)));
    assertEquals(50, status[0]);
  }

  @Test
  void ssc301006NullAndWrongSlotsRejectBeforeLoad() {
    var calls = new AtomicInteger();
    ApiProcessMain.ConfigurationLoad input =
        () -> {
          calls.incrementAndGet();
          throw new AssertionError("load before slot validation");
        };
    assertThrows(
        NullPointerException.class,
        () -> ApiProcessMain.admittedConfiguration(null, new int[] {50}));
    assertThrows(
        NullPointerException.class, () -> ApiProcessMain.admittedConfiguration(input, null));
    for (int[] status : List.of(new int[0], new int[] {50, 50})) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> ApiProcessMain.admittedConfiguration(input, status));
      assertEquals("one configuration failure status required", failure.getMessage());
    }
    assertEquals(0, calls.get());
  }

  @Test
  void ssc301007NullResultDoesNotBecomeNormal70() {
    int[] status = {50};
    var failure =
        assertThrows(
            NullPointerException.class,
            () -> ApiProcessMain.admittedConfiguration(() -> null, status));
    assertEquals("startup inputs", failure.getMessage());
    assertEquals(50, status[0]);
  }

  @Test
  void ssc301008ConcurrentCallersNeverShareFailureSlot() throws Exception {
    var input = values();
    var jobs = new ArrayList<Callable<Integer>>();
    for (int i = 0; i < 16; i++) {
      final boolean invalid = i % 2 == 0;
      jobs.add(
          () -> {
            int[] status = {50};
            if (invalid) {
              assertThrows(
                  IOException.class,
                  () ->
                      ApiProcessMain.admittedConfiguration(
                          () -> {
                            throw new IllegalArgumentException(FIXTURE_UNTRUSTED_6FC6869D);
                          },
                          status));
            } else {
              assertSame(input, ApiProcessMain.admittedConfiguration(() -> input, status).value());
            }
            return status[0];
          });
    }
    try (var executor = Executors.newFixedThreadPool(4)) {
      var results = executor.invokeAll(jobs);
      for (int i = 0; i < results.size(); i++)
        assertEquals(i % 2 == 0 ? 70 : 50, results.get(i).get());
    }
  }
}
