package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.LinuxStartupAdmission;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

/** PT-OPS-STARTADMIT-001..008. Independent literal packet; callback factory ordering, not R2. */
final class ServiceStartupAdmissionTest {
  @Test
  void monitor003CallerLockCannotBlockReadyInformationOrRelease() throws Exception {
    var fixture = new Fixture();
    fixture
        .subject()
        .execute(
            ready -> {
              try {
                CallerMonitorProbe.requireIndependent(
                    ready,
                    () -> {
                      assertEquals(Map.of("commit", "a".repeat(40)), ready.information());
                      ready.release();
                    });
              } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                throw new IOException("test owner interrupted", interrupted);
              }
            });
    assertEquals(1, fixture.releases);
    assertEquals(1, fixture.finalCloses);
  }

  static final Map<String, String> ENV =
      Map.of(
          "SCHUBERT_NK_STARTUP_ADMISSION_FD",
          "128",
          "SCHUBERT_NK_STARTUP_PROOF_FD",
          "129",
          "INVOCATION_ID",
          "11111111111111111111111111111111");
  static final String GOLDEN =
      """
      NKSTART1
      service=API
      boot_id=11111111-1111-1111-1111-111111111111
      invocation_id=11111111111111111111111111111111
      pid=42
      start_ticks=12345
      admission_fd=128
      admission_device=123
      admission_inode=456
      service_uid=200
      service_gid=201
      service_groups=200,201,202
      permit_epoch=33333333-3333-3333-3333-333333333333
      permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      release_sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      config_sha256=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      roots_sha256=dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
      broker_invocation_id=22222222222222222222222222222222
      """;

  static final class Fixture
      implements ServiceStartupAdmission.DescriptorGate, ServiceStartupAdmission.Observation {
    final List<String> order = new ArrayList<>();
    Map<String, String> env = ENV;
    String proof = GOLDEN;
    String release = "b".repeat(64);
    String config = "c".repeat(64);
    ServiceConfigFiles.Service service = ServiceConfigFiles.Service.API;
    LinuxStartupAdmission.Identity admission = new LinuxStartupAdmission.Identity(128, 123, 456);
    ChildStartupContext.Observed self =
        new ChildStartupContext.Observed(
            "11111111-1111-1111-1111-111111111111",
            42,
            12345,
            200,
            201,
            List.of(200L, 201L, 202L),
            "0::/system.slice/schubert-nk-api.service\n",
            true,
            true);
    boolean gateFails;
    boolean closeFails;
    boolean changed;
    String ioFault = "";
    RuntimeException unknown;
    Throwable readyFault;
    int captures;
    int factories;
    int releases;
    int finalCloses;

    ServiceStartupAdmission subject() {
      return new ServiceStartupAdmission(service, env, config, this, this);
    }

    public void execute(int a, int p, ServiceStartupAdmission.Admitted action) throws IOException {
      assertEquals(128, a);
      assertEquals(129, p);
      order.add("root2fd");
      try {
        if (gateFails) throw new IOException("known gate failure");
        byte[] bytes = proof.getBytes(StandardCharsets.US_ASCII);
        order.add("proofClosed");
        try {
          action.execute(
              admission,
              bytes,
              () -> {
                if (readyFault instanceof IOException io) throw io;
                if (readyFault instanceof RuntimeException runtime) throw runtime;
                if (readyFault instanceof Error error) throw error;
                releases++;
                order.add("ready-release");
              });
        } finally {
          Arrays.fill(bytes, (byte) 0);
        }
      } finally {
        finalCloses++;
        order.add("A-close");
        if (closeFails) throw new IOException("close failure");
      }
    }

    void failure(String step) throws IOException {
      if (unknown != null) throw unknown;
      if (ioFault.equals(step)) throw new IOException("PRIVATE");
    }

    public ChildStartupContext.Observed capture() throws IOException {
      order.add("capture");
      failure("capture");
      captures++;
      return changed && captures == 2
          ? new ChildStartupContext.Observed(
              self.boot(),
              self.pid(),
              self.startTicks() + 1,
              self.uid(),
              self.gid(),
              self.groups(),
              self.cgroup(),
              self.zeroCapabilities(),
              self.noNewPrivileges())
          : self;
    }

    public FixedServiceIdentity.Value identity(ServiceConfigFiles.Service service)
        throws IOException {
      assertEquals(this.service, service);
      order.add("NSS");
      failure("NSS");
      return new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L));
    }

    public String releaseHash() throws IOException {
      order.add("manifest");
      failure("manifest");
      return release;
    }

    public Map<String, String> information(String releaseHash) throws IOException {
      assertEquals("b".repeat(64), releaseHash);
      failure("information");
      return Map.of("commit", "a".repeat(40));
    }

    void run() throws IOException {
      subject()
          .execute(
              ready -> {
                factories++;
                order.add("factory");
                ready.release();
                order.add("business-cleanup");
              });
    }
  }

  static void denied(Fixture f) {
    assertThrows(IOException.class, f::run);
    assertEquals(0, f.factories);
    assertEquals(0, f.releases);
  }

  @Test
  void startadmit009PublicInfoLivesOnlyBeforeHandoff() throws Exception {
    var f = new Fixture();
    var borrowed = new java.util.concurrent.atomic.AtomicReference<ServiceStartupAdmission.Ready>();
    f.subject()
        .execute(
            ready -> {
              borrowed.set(ready);
              assertEquals(Map.of("commit", "a".repeat(40)), ready.information());
              assertThrows(
                  UnsupportedOperationException.class, () -> ready.information().put("extra", "x"));
              ready.release();
              assertThrows(IOException.class, ready::information);
            });
    assertThrows(IOException.class, borrowed.get()::information);
    var fault = new Fixture();
    fault.ioFault = "information";
    assertThrows(
        IOException.class,
        () ->
            fault
                .subject()
                .execute(
                    ready -> {
                      ready.information();
                      ready.release();
                    }));
    assertEquals(0, fault.releases);
    assertEquals(1, fault.finalCloses);
    ServiceStartupAdmission.Ready legacy = () -> {};
    assertThrows(IOException.class, legacy::information);
    assertThrows(
        IOException.class,
        () ->
            new ServiceStartupAdmission.Observation() {
              public ChildStartupContext.Observed capture() {
                return f.self;
              }

              public FixedServiceIdentity.Value identity(ServiceConfigFiles.Service ignored) {
                return new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L));
              }

              public String releaseHash() {
                return f.release;
              }
            }.information(f.release));
  }

  @Test
  void startadmit001MandatoryOrderBeforeBusinessAndReady() throws Exception {
    var f = new Fixture();
    f.run();
    assertEquals(
        List.of(
            "root2fd",
            "proofClosed",
            "capture",
            "NSS",
            "manifest",
            "capture",
            "factory",
            "ready-release",
            "business-cleanup",
            "A-close"),
        f.order);
    assertEquals(1, f.factories);
    assertEquals(1, f.releases);
    assertEquals(1, f.finalCloses);
    var configured = new Fixture();
    Object snapshot = new Object();
    configured
        .subject()
        .execute(
            () -> {
              configured.order.add("config");
              return new ServiceStartupAdmission.Configuration<>(snapshot, configured.config);
            },
            (value, ready) -> {
              assertSame(snapshot, value);
              configured.factories++;
              ready.release();
            });
    assertEquals(
        List.of(
            "root2fd",
            "proofClosed",
            "config",
            "capture",
            "NSS",
            "manifest",
            "capture",
            "ready-release",
            "A-close"),
        configured.order);
    var web = new Fixture();
    web.service = ServiceConfigFiles.Service.WEB;
    web.proof = GOLDEN.replace("service=API", "service=WEB");
    web.self =
        new ChildStartupContext.Observed(
            web.self.boot(),
            42,
            12345,
            200,
            201,
            List.of(200L, 201L, 202L),
            "0::/system.slice/schubert-nk-web.service\n",
            true,
            true);
    web.run();
    assertEquals(1, web.factories);
  }

  @Test
  void startadmit002MissingInvalidAndUntrustedDescriptorsHaveFactoryZero() {
    for (var env :
        List.of(
            Map.<String, String>of(),
            Map.of("SCHUBERT_NK_STARTUP_ADMISSION_FD", "0"),
            Map.of(
                "SCHUBERT_NK_STARTUP_ADMISSION_FD",
                "128",
                "SCHUBERT_NK_STARTUP_PROOF_FD",
                "128"))) {
      var f = new Fixture();
      f.env = env;
      denied(f);
      assertEquals(List.of(), f.order);
    }
    var f = new Fixture();
    f.gateFails = true;
    denied(f);
    assertEquals(List.of("root2fd", "A-close"), f.order);
  }

  @Test
  void startadmit003MalformedRootProofIsRedactedAndNeverObservesBusiness() {
    for (String bad :
        List.of(
            "",
            GOLDEN.replace("NKSTART1", "NKSTART0"),
            GOLDEN.replace("permit_sha256=", "other="),
            GOLDEN.replace("service=API", "service=ADMIN"))) {
      var f = new Fixture();
      f.proof = bad;
      IOException e = assertThrows(IOException.class, f::run);
      assertEquals("startup proof unavailable", e.getMessage());
      assertNull(e.getCause());
      assertEquals(0, f.factories);
      assertEquals(0, f.captures);
      assertEquals(1, f.finalCloses);
    }
  }

  @Test
  void startadmit004IndependentBindingsAndChangedKernelRefuseFactory() {
    for (String replacement :
        List.of(
            "service=WEB",
            "pid=43",
            "admission_fd=130",
            "admission_device=124",
            "config_sha256=" + "e".repeat(64),
            "release_sha256=" + "e".repeat(64))) {
      var f = new Fixture();
      String key = replacement.substring(0, replacement.indexOf('='));
      f.proof = GOLDEN.replaceAll("(?m)^" + key + "=.*$", replacement);
      denied(f);
    }
    var f = new Fixture();
    f.release = "e".repeat(64);
    denied(f);
    f = new Fixture();
    f.config = "e".repeat(64);
    denied(f);
    f = new Fixture();
    f.admission = new LinuxStartupAdmission.Identity(128, 123, 457);
    denied(f);
    f = new Fixture();
    f.changed = true;
    denied(f);
    assertEquals(2, f.captures);
  }

  @Test
  void startadmit005EveryObservationFailureAndUnknownIdentity() {
    var configFailure = new Fixture();
    assertThrows(
        IOException.class,
        () ->
            configFailure
                .subject()
                .execute(
                    () -> {
                      configFailure.order.add("config");
                      throw new IOException("PRIVATE");
                    },
                    (value, ready) -> {
                      throw new AssertionError("factory forbidden");
                    }));
    assertEquals(List.of("root2fd", "proofClosed", "config", "A-close"), configFailure.order);
    var nullConfig = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            nullConfig
                .subject()
                .execute(
                    () -> null,
                    (value, ready) -> {
                      throw new AssertionError();
                    }));
    assertEquals(1, nullConfig.finalCloses);
    var fdFailure = new Fixture();
    fdFailure.gateFails = true;
    assertThrows(
        IOException.class,
        () ->
            fdFailure
                .subject()
                .execute(
                    () -> {
                      throw new AssertionError("file forbidden");
                    },
                    (value, ready) -> {
                      throw new AssertionError();
                    }));
    for (String step : List.of("capture", "NSS", "manifest")) {
      var f = new Fixture();
      f.ioFault = step;
      denied(f);
      assertEquals(1, f.finalCloses);
    }
    var f = new Fixture();
    var unknown = new IllegalStateException("UNKNOWN");
    f.unknown = unknown;
    assertSame(unknown, assertThrows(IllegalStateException.class, f::run));
    assertEquals(0, f.factories);
    assertEquals(1, f.finalCloses);
  }

  @Test
  void startadmit006BusinessFailureCleansBeforeFinalAAndCloseNotSuccess() {
    var f = new Fixture();
    assertThrows(
        IOException.class,
        () ->
            f.subject()
                .execute(
                    ready -> {
                      f.order.add("business-cleanup");
                      throw new IOException("business failure");
                    }));
    assertEquals(
        List.of(
            "root2fd",
            "proofClosed",
            "capture",
            "NSS",
            "manifest",
            "capture",
            "business-cleanup",
            "A-close"),
        f.order);
    assertEquals(0, f.releases);
    var close = new Fixture();
    close.closeFails = true;
    assertThrows(IOException.class, close::run);
    assertEquals(1, close.finalCloses);
    var unknown = new IllegalArgumentException("UNKNOWN");
    var u = new Fixture();
    assertSame(
        unknown,
        assertThrows(
            IllegalArgumentException.class,
            () ->
                u.subject()
                    .execute(
                        ready -> {
                          throw unknown;
                        })));
    assertEquals(1, u.finalCloses);
  }

  @Test
  void startadmit007NullConstructorHashAndDescriptorNames() {
    var f = new Fixture();
    assertThrows(
        NullPointerException.class, () -> new ServiceStartupAdmission(null, ENV, f.config, f, f));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceStartupAdmission(f.service, null, f.config, f, f));
    assertThrows(
        NullPointerException.class, () -> new ServiceStartupAdmission(f.service, ENV, null, f, f));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceStartupAdmission(f.service, ENV, f.config, null, f));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceStartupAdmission(f.service, ENV, f.config, f, null));
    assertThrows(NullPointerException.class, () -> f.subject().execute(null));
    for (String hash : List.of("", "C".repeat(64), "c".repeat(63), "c".repeat(65)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new ServiceStartupAdmission(f.service, ENV, hash, f, f));
    assertTrue(ChildStartupContext.isDescriptorKey("SCHUBERT_NK_STARTUP_ADMISSION_FD"));
    assertTrue(ChildStartupContext.isDescriptorKey("SCHUBERT_NK_STARTUP_PROOF_FD"));
    for (String alias :
        List.of(
            "schubert_nk_startup_proof_fd", "SCHUBERT_NK_STARTUP_TOKEN", "SCHUBERT_NK_CONFIG_DIR"))
      assertFalse(ChildStartupContext.isDescriptorKey(alias));
    assertThrows(NullPointerException.class, () -> ChildStartupContext.isDescriptorKey(null));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceStartupAdmission.Configuration<>(null, f.config));
    assertThrows(
        NullPointerException.class,
        () -> new ServiceStartupAdmission.Configuration<>(Boolean.TRUE, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ServiceStartupAdmission.Configuration<>(Boolean.TRUE, "bad"));
    assertThrows(NullPointerException.class, () -> f.subject().execute(null, (value, ready) -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            f.subject()
                .execute(
                    () -> new ServiceStartupAdmission.Configuration<>(Boolean.TRUE, f.config),
                    null));
    assertThrows(
        IllegalStateException.class,
        () ->
            ServiceStartupAdmission.create(f.service, ENV)
                .execute(
                    ready -> {
                      throw new AssertionError();
                    }));
  }

  @Test
  void startadmit008ConcurrentScopesAndNativeFailureNoBusiness() throws Exception {
    try (var executor = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<Fixture>>();
      for (int i = 0; i < 32; i++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  f.run();
                  return f;
                }));
      for (var future : futures) {
        var f = future.get();
        assertEquals(1, f.factories);
        assertEquals(1, f.finalCloses);
      }
    }
    assertThrows(
        IOException.class,
        () ->
            ServiceStartupAdmission.create(
                    ServiceConfigFiles.Service.API,
                    Map.of(
                        "SCHUBERT_NK_STARTUP_ADMISSION_FD",
                        "65534",
                        "SCHUBERT_NK_STARTUP_PROOF_FD",
                        "65535",
                        "INVOCATION_ID",
                        "11111111111111111111111111111111"),
                    "c".repeat(64))
                .execute(
                    ready -> {
                      throw new AssertionError("no inherited root FD");
                    }));
    var nativeIo = new ServiceStartupAdmission.NativeObservation();
    assertTrue(nativeIo.capture().pid() > 1);
    assertThrows(IOException.class, () -> nativeIo.identity(ServiceConfigFiles.Service.API));
    assertThrows(IOException.class, nativeIo::releaseHash);
  }

  @Test
  void startadmit009NormalReturnWithoutReadyIsNotAcceptance() {
    var direct = new Fixture();
    assertThrows(IOException.class, () -> direct.subject().execute(ready -> {}));
    assertEquals(0, direct.releases);
    assertEquals(1, direct.finalCloses);

    var configured = new Fixture();
    assertThrows(
        IOException.class,
        () ->
            configured
                .subject()
                .execute(
                    () ->
                        new ServiceStartupAdmission.Configuration<>(
                            Boolean.TRUE, configured.config),
                    (value, ready) -> assertTrue(value)));
    assertEquals(0, configured.releases);
    assertEquals(1, configured.finalCloses);

    var web = new Fixture();
    web.service = ServiceConfigFiles.Service.WEB;
    web.proof = GOLDEN.replace("service=API", "service=WEB");
    web.self =
        new ChildStartupContext.Observed(
            web.self.boot(),
            web.self.pid(),
            web.self.startTicks(),
            web.self.uid(),
            web.self.gid(),
            web.self.groups(),
            "0::/system.slice/schubert-nk-web.service\n",
            true,
            true);
    assertThrows(IOException.class, () -> web.subject().execute(ready -> {}));
    assertEquals(0, web.releases);
    assertEquals(1, web.finalCloses);
  }

  @Test
  void startadmit010ReadyCapabilityCannotBeReusedOrEscaped() {
    var duplicate = new Fixture();
    assertThrows(
        IOException.class,
        () ->
            duplicate
                .subject()
                .execute(
                    ready -> {
                      ready.release();
                      assertThrows(IOException.class, ready::release);
                    }));
    assertEquals(1, duplicate.releases);
    assertEquals(1, duplicate.finalCloses);

    var late = new Fixture();
    ServiceStartupAdmission.Ready[] escaped = {null};
    assertThrows(
        IOException.class,
        () ->
            late.subject()
                .execute(
                    ready -> {
                      escaped[0] = ready;
                    }));
    assertNotNull(escaped[0]);
    assertThrows(IOException.class, escaped[0]::release);
    assertEquals(0, late.releases);
    assertEquals(1, late.finalCloses);

    var completed = new Fixture();
    ServiceStartupAdmission.Ready[] completedCapability = {null};
    assertDoesNotThrow(
        () ->
            completed
                .subject()
                .execute(
                    ready -> {
                      ready.release();
                      completedCapability[0] = ready;
                    }));
    assertThrows(IOException.class, completedCapability[0]::release);
    assertEquals(1, completed.releases);
    assertEquals(1, completed.finalCloses);

    for (Throwable fault :
        List.of(
            new IOException("close failed"),
            new IllegalStateException("runtime"),
            new AssertionError("error"))) {
      var failed = new Fixture();
      failed.readyFault = fault;
      assertThrows(
          IOException.class,
          () ->
              failed
                  .subject()
                  .execute(
                      ready -> assertSame(fault, assertThrows(Throwable.class, ready::release))));
      assertEquals(0, failed.releases);
      assertEquals(1, failed.finalCloses);
    }
  }
}
