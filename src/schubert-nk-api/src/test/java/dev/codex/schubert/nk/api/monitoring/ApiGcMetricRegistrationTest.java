package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** APIGC001..014/1785: exact owner order/identity, fresh own SDK objects only, no forced GC. */
class ApiGcMetricRegistrationTest {
  private final ApiGcMetricRegistration registration = new ApiGcMetricRegistration();

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final AtomicInteger reads = new AtomicInteger();
    final AtomicInteger closeInvocations = new AtomicInteger();

    Registry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }

    public boolean isClosed() {
      reads.incrementAndGet();
      return super.isClosed();
    }

    public List<io.micrometer.core.instrument.Meter> getMeters() {
      reads.incrementAndGet();
      return super.getMeters();
    }

    public void close() {
      closeInvocations.incrementAndGet();
      super.close();
    }
  }

  private static final class Fake extends JvmGcMetrics {
    final AtomicInteger bindInvocations = new AtomicInteger();
    final AtomicInteger closeInvocations = new AtomicInteger();
    boolean closeConfirmed;
    Consumer<MeterRegistry> onBindCallback = source -> {};
    Runnable onCloseCallback = () -> {};

    Fake() {
      super(Tags.of("service", "API"));
    }

    public void bindTo(MeterRegistry source) {
      bindInvocations.incrementAndGet();
      onBindCallback.accept(source);
    }

    public void close() {
      closeConfirmed = false;
      closeInvocations.incrementAndGet();
      onCloseCallback.run();
      closeConfirmed = true;
    }
  }

  private static <T> T fail(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  @Test
  void apigc001DefaultSdkIsOwnedAndClosedBeforeBorrowedRegistry() {
    var owned = new ArrayList<JvmGcMetrics>();
    try (var source = new Registry()) {
      try {
        registration.bind(source, "DEBUG", owned::add);
        assertEquals(1, owned.size());
        assertNotNull(owned.getFirst());
        assertFalse(source.getMeters().isEmpty());
        for (var meter : source.getMeters()) {
          assertTrue(meter.getId().getName().startsWith("jvm."));
          assertEquals("API", meter.getId().getTag("service"));
        }
        assertFalse(source.isClosed());
        assertEquals(0, source.closeInvocations.get());
      } finally {
        for (var resource : owned) resource.close();
      }
      assertFalse(source.isClosed());
      assertEquals(0, source.closeInvocations.get());
    }
  }

  @Test
  void apigc002StandardIsLazyForSourceFactoryAndOwner() {
    try (var source = new Registry()) {
      var factories = new AtomicInteger();
      var owners = new AtomicInteger();
      source.reads.set(0);
      ApiGcMetricRegistration.install(
          source,
          "STANDARD",
          resource -> {
            owners.incrementAndGet();
            throw new AssertionError("not own");
          },
          () -> {
            factories.incrementAndGet();
            throw new AssertionError("not construct");
          });
      registration.bind(
          source,
          "STANDARD",
          resource -> {
            throw new AssertionError("not own");
          });
      assertEquals(0, factories.get());
      assertEquals(0, owners.get());
      assertEquals(0, source.reads.get());
      assertEquals(0, source.closeInvocations.get());
    }
  }

  @Test
  void apigc003FactoryOwnerBindOrderAndSameHandle() {
    try (var source = new Registry()) {
      var events = new ArrayList<String>();
      var owned = new ArrayList<JvmGcMetrics>();
      var resource = new Fake();
      try {

        resource.onBindCallback =
            actual -> {
              assertSame(source, actual);
              assertEquals(List.of(resource), owned);
              events.add("BIND");
            };
        resource.onCloseCallback = () -> events.add("CLOSE");
        ApiGcMetricRegistration.install(
            source,
            "DEBUG",
            value -> {
              assertSame(resource, value);
              events.add("OWNER");
              return owned.add(value);
            },
            () -> {
              events.add("FACTORY");
              return resource;
            });
        assertEquals(List.of("FACTORY", "OWNER", "BIND"), events);
        assertEquals(1, resource.bindInvocations.get());
        assertEquals(0, resource.closeInvocations.get());
        owned.forEach(JvmGcMetrics::close);
        assertEquals(List.of("FACTORY", "OWNER", "BIND", "CLOSE"), events);
        assertEquals(1, resource.closeInvocations.get());
        assertFalse(source.isClosed());

      } finally {
        if (!resource.closeConfirmed) resource.close();
      }
    }
  }

  @Test
  void apigc004NullBoundariesFailBeforeActivation() {
    assertThrows(
        NullPointerException.class, () -> registration.bind(null, "STANDARD", resource -> true));
    try (var source = new Registry()) {
      assertThrows(
          NullPointerException.class, () -> registration.bind(source, null, resource -> true));
      assertThrows(NullPointerException.class, () -> registration.bind(source, "STANDARD", null));
      assertThrows(
          NullPointerException.class,
          () -> ApiGcMetricRegistration.install(source, "DEBUG", resource -> true, null));
      assertEquals(0, source.closeInvocations.get());
    }
  }

  @Test
  void apigc005UnknownModesNeverInspectSourceOrCallbacks() {
    try (var source = new Registry()) {
      var calls = new AtomicInteger();
      source.reads.set(0);
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN")) {
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () ->
                        ApiGcMetricRegistration.install(
                            source,
                            mode,
                            resource -> {
                              calls.incrementAndGet();
                              throw new AssertionError("not own");
                            },
                            () -> {
                              calls.incrementAndGet();
                              throw new AssertionError("not construct");
                            }))
                .getMessage());
      }
      assertEquals(0, calls.get());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void apigc006ClosedDebugFailsBeforeFactoryAndOwner() {
    var source = new Registry();
    source.close();
    var calls = new AtomicInteger();
    assertThrows(
        IllegalStateException.class,
        () ->
            ApiGcMetricRegistration.install(
                source,
                "DEBUG",
                resource -> {
                  calls.incrementAndGet();
                  return true;
                },
                () -> {
                  calls.incrementAndGet();
                  return new Fake();
                }));
    assertEquals(0, calls.get());
    assertEquals(1, source.closeInvocations.get());
    assertTrue(source.isClosed());
    source.reads.set(0);
    registration.bind(
        source,
        "STANDARD",
        resource -> {
          throw new AssertionError("not own");
        });
    assertEquals(0, source.reads.get());
  }

  @Test
  void apigc007NullFactoryResultIsNeverAcknowledged() {
    try (var source = new Registry()) {
      var calls = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () ->
              ApiGcMetricRegistration.install(
                  source,
                  "DEBUG",
                  resource -> {
                    calls.incrementAndGet();
                    return true;
                  },
                  () -> null));
      assertEquals(0, calls.get());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void apigc008FactoryRuntimeAndErrorIdentityRetained() {
    try (var source = new Registry()) {
      for (Throwable failure :
          List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
        var owners = new AtomicInteger();
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    ApiGcMetricRegistration.install(
                        source,
                        "DEBUG",
                        resource -> {
                          owners.incrementAndGet();
                          return true;
                        },
                        () -> fail(failure))));
        assertEquals(0, owners.get());
        assertFalse(source.isClosed());
        assertEquals(0, source.closeInvocations.get());
      }
    }
  }

  @Test
  void apigc009OwnerRejectMeansNoBindOrImplicitClose() {
    try (var source = new Registry()) {
      var resource = new Fake();
      try {

        var owners = new AtomicInteger();
        assertEquals(
            "GC binding owner unavailable",
            assertThrows(
                    IllegalStateException.class,
                    () ->
                        ApiGcMetricRegistration.install(
                            source,
                            "DEBUG",
                            value -> {
                              assertSame(resource, value);
                              owners.incrementAndGet();
                              return false;
                            },
                            () -> resource))
                .getMessage());
        assertEquals(1, owners.get());
        assertEquals(0, resource.bindInvocations.get());
        assertEquals(0, resource.closeInvocations.get());
        assertFalse(source.isClosed());

      } finally {
        if (!resource.closeConfirmed) resource.close();
      }
    }
  }

  @Test
  void apigc010OwnerRuntimeAndErrorNeverActivateOrAutoClose() {
    try (var source = new Registry()) {
      for (Throwable failure :
          List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
        var resource = new Fake();
        try {

          assertSame(
              failure,
              assertThrows(
                  failure.getClass(),
                  () ->
                      ApiGcMetricRegistration.install(
                          source, "DEBUG", value -> fail(failure), () -> resource)));
          assertEquals(0, resource.bindInvocations.get());
          assertEquals(0, resource.closeInvocations.get());
          assertFalse(source.isClosed());

        } finally {
          if (!resource.closeConfirmed) resource.close();
        }
      }
    }
  }

  @Test
  void apigc011BindFailureLeavesExactHandleInAcknowledgedOwner() {
    try (var source = new Registry()) {
      for (Throwable failure :
          List.of(new IllegalStateException("fixture"), new AssertionError("fixture"))) {
        var resource = new Fake();
        try {

          var owned = new ArrayList<JvmGcMetrics>();
          resource.onBindCallback =
              actual -> {
                assertSame(source, actual);
                assertEquals(List.of(resource), owned);
                fail(failure);
              };
          assertSame(
              failure,
              assertThrows(
                  failure.getClass(),
                  () ->
                      ApiGcMetricRegistration.install(
                          source, "DEBUG", owned::add, () -> resource)));
          assertEquals(List.of(resource), owned);
          assertEquals(1, resource.bindInvocations.get());
          assertEquals(0, resource.closeInvocations.get());
          owned.forEach(JvmGcMetrics::close);
          assertEquals(1, resource.closeInvocations.get());
          assertFalse(source.isClosed());
          assertEquals(0, source.closeInvocations.get());

        } finally {
          if (!resource.closeConfirmed) resource.close();
        }
      }
    }
  }

  @Test
  void apigc012SameInstallerDoesNotMixTwoOwnerScopes() {
    try (var first = new Registry();
        var other = new Registry()) {
      var one = new Fake();
      try {

        var two = new Fake();
        try {

          var owners1 = new ArrayList<JvmGcMetrics>();
          var owners2 = new ArrayList<JvmGcMetrics>();
          one.onBindCallback = actual -> assertSame(first, actual);
          two.onBindCallback = actual -> assertSame(other, actual);
          ApiGcMetricRegistration.install(first, "DEBUG", owners1::add, () -> one);
          ApiGcMetricRegistration.install(other, "DEBUG", owners2::add, () -> two);
          assertEquals(List.of(one), owners1);
          assertEquals(List.of(two), owners2);
          owners1.forEach(JvmGcMetrics::close);
          assertEquals(1, one.closeInvocations.get());
          assertEquals(0, two.closeInvocations.get());
          owners2.forEach(JvmGcMetrics::close);
          assertEquals(1, two.closeInvocations.get());
          assertFalse(first.isClosed());
          assertFalse(other.isClosed());

        } finally {
          if (!two.closeConfirmed) two.close();
        }

      } finally {
        if (!one.closeConfirmed) one.close();
      }
    }
  }

  @Test
  void apigc013FiniteIndependentConcurrentOwnerScopes() throws Exception {
    try (var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      var total = new AtomicInteger();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  try (var source = new Registry()) {
                    var resource = new Fake();
                    try {

                      var owned = new ArrayList<JvmGcMetrics>();
                      resource.onBindCallback =
                          actual -> {
                            assertSame(source, actual);
                            assertEquals(List.of(resource), owned);
                            total.incrementAndGet();
                          };
                      ApiGcMetricRegistration.install(source, "DEBUG", owned::add, () -> resource);
                      assertEquals(1, resource.bindInvocations.get());
                      assertEquals(0, resource.closeInvocations.get());
                      owned.forEach(JvmGcMetrics::close);
                      assertEquals(1, resource.closeInvocations.get());
                      assertFalse(source.isClosed());

                    } finally {
                      if (!resource.closeConfirmed) resource.close();
                    }
                  }
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(64, total.get());
    }
  }

  @Test
  void apigc014RetainThenRejectOrThrowKeepsCallerCleanupWithoutActivation() {
    try (var source = new Registry()) {
      for (boolean throwsFailure : List.of(false, true)) {
        var resource = new Fake();
        try {

          var owned = new ArrayList<JvmGcMetrics>();
          var failure = new IllegalStateException("fixture");
          var actual =
              assertThrows(
                  IllegalStateException.class,
                  () ->
                      ApiGcMetricRegistration.install(
                          source,
                          "DEBUG",
                          value -> {
                            owned.add(value);
                            if (throwsFailure) throw failure;
                            return false;
                          },
                          () -> resource));
          if (throwsFailure) assertSame(failure, actual);
          else assertEquals("GC binding owner unavailable", actual.getMessage());
          assertEquals(List.of(resource), owned);
          assertEquals(0, resource.bindInvocations.get());
          assertEquals(0, resource.closeInvocations.get());
          owned.forEach(JvmGcMetrics::close);
          assertEquals(1, resource.closeInvocations.get());
          assertFalse(source.isClosed());

        } finally {
          if (!resource.closeConfirmed) resource.close();
        }
      }
    }
  }

  @Test
  void apigc015ConfirmedFixtureCloseIsNotRepeatedByCleanupGuard() {
    var resource = new Fake();
    try {
      assertFalse(resource.closeConfirmed);
      resource.close();
      assertTrue(resource.closeConfirmed);
      if (!resource.closeConfirmed) resource.close();
      assertEquals(1, resource.closeInvocations.get());
    } finally {
      if (!resource.closeConfirmed) resource.close();
    }
  }

  @Test
  void apigc016FailedFixtureCloseRemainsUnconfirmedUntilExplicitRetry() {
    for (boolean priorSuccess : List.of(false, true)) {
      for (Throwable failure :
          List.of(
              new IllegalStateException("cleanup runtime fixture"),
              new AssertionError("cleanup fatal fixture"))) {
        var resource = new Fake();
        try {
          if (priorSuccess) resource.close();
          resource.onCloseCallback = () -> fail(failure);
          assertSame(failure, assertThrows(failure.getClass(), resource::close));
          assertFalse(resource.closeConfirmed);
          assertEquals(priorSuccess ? 2 : 1, resource.closeInvocations.get());
          resource.onCloseCallback = () -> {};
          if (!resource.closeConfirmed) resource.close();
          assertTrue(resource.closeConfirmed);
          assertEquals(priorSuccess ? 3 : 2, resource.closeInvocations.get());
        } finally {
          resource.onCloseCallback = () -> {};
          if (!resource.closeConfirmed) resource.close();
        }
      }
    }
  }
}
