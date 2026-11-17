package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.storage.StorageRootLayout;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** ROOTBOM001..009. Package policy ports are synthetic, NOT actual root/native admission. */
public final class RootReleaseAdmissionTest {
  // ROOTCFG002/ISSUERCFG002: independently written SS343 default canonical bytes.
  // No production parser, map or encoder generates this expected value (BUG424/YKT335).
  private static String independentApiDefaultHash() throws Exception {
    String canonical =
        "nk.api.async-consumers=1\n"
            + "nk.api.storage.asset-manifest-entries=59627\n"
            + "nk.api.storage.asset-root=/srv/schubert-nk/data/assets\n"
            + "nk.api.storage.transfer-root=/srv/schubert-nk/data/transfer\n"
            + "nk.api.sync-consumers.initial=4\n"
            + "nk.api.sync-consumers.max=8\n"
            + "nk.db.connect-timeout=3s\n"
            + "nk.db.pool.api.max=8\n"
            + "nk.db.pool.api.min=2\n"
            + "nk.db.url=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n"
            + "nk.inbox.reference-retention=24h\n"
            + "nk.inbox.update-retention=7d\n"
            + "nk.monitoring.mode=STANDARD\n"
            + "nk.mq.async-work=nk.async.work\n"
            + "nk.mq.dlq=nk.dead.letter\n"
            + "nk.mq.expiry=nk.expiry\n"
            + "nk.mq.sync-reply=nk.sync.reply.web\n"
            + "nk.mq.sync-request=nk.sync.request\n"
            + "nk.mq.url=tcp://127.0.0.1:61616\n"
            + "nk.mq.web-log=nk.web.log\n"
            + "nk.outbox.sent-retention=7d\n"
            + "nk.protocol.version=001\n"
            + "nk.time.display-zone=Asia/Tokyo\n";
    return HexFormat.of()
        .formatHex(
            java.security.MessageDigest.getInstance("SHA-256")
                .digest(canonical.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
  }

  @TempDir Path publicOsDirectory;
  static final Map<String, String> PLATFORM =
      Map.of("osId", "ubuntu", "osVersion", "26.04", "architecture", "x86_64", "javaFeature", "25");
  static final Map<String, String> BUILD =
      Map.of("jdkVendor", "PUBLIC VENDOR", "jdkVersion", "25.0.4");
  static final Map<String, String> ACTUAL =
      Map.of(
          "osId",
          "ubuntu",
          "osVersion",
          "26.04",
          "architecture",
          "x86_64",
          "javaFeature",
          "25",
          "jdkVendor",
          "PUBLIC VENDOR",
          "jdkVersion",
          "25.0.4");

  static StartupReleaseManifest.Contents literal() {
    return new StartupReleaseManifest.Contents(
        "PG314",
        "a".repeat(64),
        List.of(
            new SchemaHistoryAdmission.Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true),
            new SchemaHistoryAdmission.Row(1, "001", "SQL", "V001__first.sql", -690524359, true)),
        BUILD,
        PLATFORM);
  }

  @Test
  void rootBom010ActualSchemaAndRuntimeSurviveOwnersOnlyAsImmutableData() throws Exception {
    var fixture = new Fixture();
    var subject = fixture.subject();
    var actual =
        subject.inspectMorningDatabase(connection(fixture.events, false), fixture.expected);
    assertEquals(
        List.of(
            new SchemaHistoryAdmission.Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true),
            new SchemaHistoryAdmission.Row(1, "001", "SQL", "V001__first.sql", -690524359, true)),
        actual.schemaRows());
    assertEquals(ACTUAL, actual.runtime());
    assertNotSame(actual.contents().migrations().getFirst(), actual.schemaRows().getFirst());
    assertThrows(UnsupportedOperationException.class, actual.schemaRows()::clear);
    assertThrows(UnsupportedOperationException.class, () -> actual.runtime().put("osId", "wrong"));
    assertTrue(fixture.events.contains("rows.close"));
    assertTrue(fixture.events.contains("statement.close"));
    assertFalse(actual.toString().contains("PUBLIC VENDOR"));
    assertThrows(
        NullPointerException.class,
        () -> new RootReleaseAdmission.DatabaseInspection(null, List.of(), Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new RootReleaseAdmission.DatabaseInspection(literal(), null, Map.of()));
    assertThrows(
        NullPointerException.class,
        () -> new RootReleaseAdmission.DatabaseInspection(literal(), List.of(), null));
  }

  static final class Fixture {
    final RootStartupContextTest.Fixture kernel = new RootStartupContextTest.Fixture();
    final RootStartupContext context;
    final RootStartupContext.Snapshot expected;
    final List<String> events = new ArrayList<>();
    int loads;

    Fixture() throws IOException {
      this(RootStartupContext.Service.MORNING);
    }

    Fixture(RootStartupContext.Service service) throws IOException {
      kernel.group = "0::/system.slice/" + service.unit() + "\n";
      kernel.unitValues = RootStartupContextTest.unit(service);
      context = new RootStartupContext(kernel);
      expected = context.capture(service);
    }

    RootReleaseAdmission subject() throws IOException {
      return RootReleaseAdmission.create(
          context,
          expected,
          () -> {
            events.add("release-all-closed");
            loads++;
            return literal();
          },
          () -> {
            events.add("platform");
            return ACTUAL;
          });
    }
  }

  @Test
  void rootServiceInputsRemainFixedActorAndUseIndependentSchemaYamlVectors() throws Exception {
    for (var actor : List.of(RootStartupContext.Service.API, RootStartupContext.Service.WEB)) {
      var f = new Fixture(actor);
      var subject = f.subject();
      var database = subject.inspectServiceDatabase(connection(f.events, false), f.expected);
      assertEquals(literal().migrations(), database.schemaRows());
      assertEquals(ACTUAL, database.runtime());
      assertTrue(f.events.contains("statement.close") && f.events.contains("rows.close"));
      var config =
          subject.inspectServiceConfigurations(service -> new ServiceConfigFiles.Contents("", ""));
      assertEquals(independentApiDefaultHash(), config.apiSha256());
      assertEquals(
          "98cfeb71e1c4cb5a0805975b3efa3cb52ec89ca48f739b5a15c73a24a1fc22b8", config.webSha256());
      assertThrows(
          IOException.class,
          () -> subject.inspectConfigurations(service -> fail("Morning-only before file IO")));
      assertThrows(
          IOException.class,
          () -> subject.inspectMorningDatabase(connection(f.events, false), f.expected));
      var other =
          new Fixture(
              actor == RootStartupContext.Service.API
                  ? RootStartupContext.Service.WEB
                  : RootStartupContext.Service.API);
      assertThrows(
          IOException.class,
          () -> subject.inspectServiceDatabase(connection(f.events, false), other.expected));
      assertThrows(
          NullPointerException.class, () -> subject.inspectServiceDatabase(null, f.expected));
      assertThrows(
          NullPointerException.class,
          () -> subject.inspectServiceDatabase(connection(f.events, false), null));
      assertThrows(NullPointerException.class, () -> subject.inspectServiceConfigurations(null));
      assertThrows(NullPointerException.class, () -> subject.recheckServiceConfigurations(null));
    }
    for (var actor :
        List.of(
            RootStartupContext.Service.MORNING,
            RootStartupContext.Service.CLEANUP,
            RootStartupContext.Service.EXPIRY)) {
      var f = new Fixture(actor);
      var subject = f.subject();
      assertThrows(
          IOException.class,
          () -> subject.inspectServiceConfigurations(service -> fail("actor before file IO")));
      assertThrows(
          IOException.class,
          () -> subject.inspectServiceDatabase(connection(f.events, false), f.expected));
      assertFalse(f.events.contains("query"));
    }
  }

  /** Test-only closed literal release; its two-row schema intentionally refuses the real DB. */
  public record CleanupInputs(
      RootStartupContext context,
      RootStartupContext.Snapshot snapshot,
      RootReleaseAdmission release,
      AtomicInteger reads) {}

  public static CleanupInputs syntheticCleanup() throws IOException {
    return syntheticCleanup(literal().migrations());
  }

  public static CleanupInputs syntheticCleanup(List<SchemaHistoryAdmission.Row> migrations)
      throws IOException {
    return syntheticChild(RootStartupContext.Service.CLEANUP, migrations);
  }

  /** Test-only Expiry actor; production Root/Unit/source admission is never bypassed. */
  public static CleanupInputs syntheticExpiry() throws IOException {
    return syntheticExpiry(literal().migrations());
  }

  public static CleanupInputs syntheticExpiry(List<SchemaHistoryAdmission.Row> migrations)
      throws IOException {
    return syntheticChild(RootStartupContext.Service.EXPIRY, migrations);
  }

  private static CleanupInputs syntheticChild(
      RootStartupContext.Service service, List<SchemaHistoryAdmission.Row> migrations)
      throws IOException {
    var fixture = new Fixture(service);
    var reads = new AtomicInteger();
    var admission =
        RootReleaseAdmission.create(
            fixture.context,
            fixture.expected,
            () -> {
              reads.incrementAndGet();
              return new StartupReleaseManifest.Contents(
                  "PG314", "a".repeat(64), migrations, BUILD, PLATFORM);
            },
            () -> ACTUAL);
    return new CleanupInputs(fixture.context, fixture.expected, admission, reads);
  }

  @Test
  void rootBom009CleanupMustUseOwnSnapshotAndFreshSchema() throws Exception {
    var f = new Fixture(RootStartupContext.Service.CLEANUP);
    var subject = f.subject();
    assertEquals(1, f.loads);
    subject.verifyCleanup(connection(f.events, false), f.expected);
    assertEquals(2, f.loads);
    assertEquals(1, f.events.stream().filter("query"::equals).count());
    int events = f.events.size();
    assertThrows(
        IOException.class, () -> subject.verifyMorning(connection(f.events, false), f.expected));
    assertEquals(events, f.events.size());
    var morning = new Fixture();
    var morningSubject = morning.subject();
    assertThrows(
        IOException.class,
        () -> morningSubject.verifyCleanup(connection(morning.events, false), morning.expected));
    assertFalse(morning.events.contains("query"));
    assertThrows(NullPointerException.class, () -> subject.verifyCleanup(null, f.expected));
    assertThrows(
        NullPointerException.class, () -> subject.verifyCleanup(connection(f.events, false), null));
    f.kernel.unitValues = f.kernel.unitValues.replace("MainPID=42", "MainPID=43");
    assertThrows(
        IOException.class, () -> subject.verifyCleanup(connection(f.events, false), f.expected));
    assertEquals(events, f.events.size());
  }

  @Test
  void issuerCfg002UsesSharedStrictEffectiveVectorsAndRawRereadNotBomTemplateHash()
      throws Exception {
    var f = new Fixture();
    var subject = f.subject();
    var yaml =
        new java.util.concurrent.atomic.AtomicReference<>(new ServiceConfigFiles.Contents("", ""));
    NonSecretConfigSource source = service -> yaml.get();
    var actual = subject.inspectConfigurations(source);
    // Independent literal/JCA vector, not a production parser/encoder output.
    assertEquals(independentApiDefaultHash(), actual.apiSha256());
    assertEquals(
        "98cfeb71e1c4cb5a0805975b3efa3cb52ec89ca48f739b5a15c73a24a1fc22b8", actual.webSha256());
    assertEquals(
        new StorageRootLayout(
            Path.of("/srv/schubert-nk/data/assets"),
            Path.of("/srv/schubert-nk/data/transfer"),
            Path.of("/srv/schubert-nk/backup"),
            Path.of("/var/log/schubert-nk"),
            Path.of("/var/lib/schubert-nk/artemis"),
            Path.of("/srv/schubert-nk/staging")),
        actual.roots());
    assertEquals("EffectiveConfigurations[non-secret=<redacted>]", actual.toString());
    subject.recheckConfigurations(actual, source);
    yaml.set(new ServiceConfigFiles.Contents("# public comment\nnk.protocol.version: '001'\n", ""));
    var sameEffective = subject.inspectConfigurations(source);
    assertEquals(actual.apiSha256(), sameEffective.apiSha256());
    assertEquals(actual.webSha256(), sameEffective.webSha256());
    assertThrows(IOException.class, () -> subject.recheckConfigurations(actual, source));
    assertThrows(
        IOException.class,
        () ->
            subject.inspectConfigurations(
                service -> new ServiceConfigFiles.Contents(service.name(), "")));
    assertThrows(
        IOException.class,
        () ->
            subject.inspectConfigurations(
                service -> new ServiceConfigFiles.Contents("unknown: value\n", "")));
    assertThrows(
        IOException.class,
        () ->
            subject.inspectConfigurations(
                service ->
                    new ServiceConfigFiles.Contents(
                        "",
                        service == ServiceConfigFiles.Service.API
                            ? "nk.api.storage.asset-root: /var/log/schubert-nk\n"
                            : "nk.web.storage.asset-root: /var/log/schubert-nk\n")));
    assertThrows(
        IOException.class,
        () ->
            subject.inspectConfigurations(
                service ->
                    new ServiceConfigFiles.Contents(
                        "",
                        service == ServiceConfigFiles.Service.API
                            ? "nk.api.storage.asset-root: /srv/a\n"
                            : "nk.web.storage.asset-root: /srv/b\n")));
    assertThrows(
        IOException.class,
        () ->
            subject.inspectConfigurations(
                service ->
                    new ServiceConfigFiles.Contents(
                        "",
                        service == ServiceConfigFiles.Service.API
                            ? "nk.api.storage.transfer-root: /srv/a\n"
                            : "nk.web.storage.transfer-root: /srv/b\n")));
    assertThrows(NullPointerException.class, () -> subject.inspectConfigurations(null));
    assertThrows(NullPointerException.class, () -> subject.inspectConfigurations(service -> null));
    assertThrows(NullPointerException.class, () -> subject.recheckConfigurations(null, source));
    var unknown = new IllegalStateException("PUBLIC UNKNOWN");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                subject.inspectConfigurations(
                    service -> {
                      throw unknown;
                    })));
    var wrong = new Fixture(RootStartupContext.Service.CLEANUP).subject();
    assertThrows(
        IOException.class,
        () -> wrong.inspectConfigurations(service -> fail("actor before file IO")));
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  static Connection connection(List<String> events, boolean incorrect) {
    var position = new AtomicInteger(-1);
    ResultSet rows =
        proxy(
            ResultSet.class,
            (p, m, a) -> {
              if (m.getName().equals("close")) {
                events.add("rows.close");
                return null;
              }
              if (m.getName().equals("next")) return position.incrementAndGet() < 2;
              String key = (String) a[0];
              boolean schema = position.get() == 0;
              return switch (key) {
                case "installed_rank" -> position.get();
                case "version" -> schema ? null : "001";
                case "type" -> schema ? "SCHEMA" : "SQL";
                case "script" -> schema ? "\"schubert_meta\"" : "V001__first.sql";
                case "checksum" -> schema ? null : Integer.valueOf(incorrect ? 0 : -690524359);
                case "success" -> true;
                default -> throw new AssertionError(key);
              };
            });
    PreparedStatement statement =
        proxy(
            PreparedStatement.class,
            (p, m, a) -> {
              return switch (m.getName()) {
                case "close" -> {
                  events.add("statement.close");
                  yield null;
                }
                case "setQueryTimeout" -> {
                  assertEquals(5, a[0]);
                  yield null;
                }
                case "executeQuery" -> {
                  events.add("query");
                  yield rows;
                }
                default -> throw new AssertionError(m.getName());
              };
            });
    return proxy(
        Connection.class,
        (p, m, a) -> {
          assertEquals(
              "prepareStatement", m.getName(), "borrowed connection never configured/closed");
          assertEquals(
              "select installed_rank,version,type,script,checksum,success from schubert_meta.startup_schema_history() order by installed_rank",
              a[0]);
          events.add("prepare");
          return statement;
        });
  }

  @Test
  void rootBom001ClosedLoaderAndFreshBeforeEverySchema() throws Exception {
    var f = new Fixture();
    var subject = f.subject();
    assertEquals(List.of("release-all-closed", "platform"), f.events);
    subject.verifyMorning(connection(f.events, false), f.expected);
    assertEquals(2, f.loads);
    assertEquals(
        List.of(
            "release-all-closed",
            "platform",
            "release-all-closed",
            "platform",
            "prepare",
            "query",
            "rows.close",
            "statement.close"),
        f.events);
  }

  @Test
  void rootBom002NoPublicClaimsOrBooleanAuthority() throws Exception {
    assertEquals(0, RootReleaseAdmission.class.getConstructors().length);
    var factories =
        Arrays.stream(RootReleaseAdmission.class.getMethods())
            .filter(m -> m.getName().equals("create"))
            .toList();
    assertEquals(1, factories.size());
    assertArrayEquals(
        new Class<?>[] {RootStartupContext.class, RootStartupContext.Snapshot.class},
        factories.getFirst().getParameterTypes());
    var f = new Fixture();
    assertThrows(
        IOException.class,
        () -> RootReleaseAdmission.create(RootStartupContext.create(), f.expected));
    assertThrows(NullPointerException.class, () -> RootReleaseAdmission.create(null, f.expected));
    assertThrows(NullPointerException.class, () -> RootReleaseAdmission.create(f.context, null));
  }

  @Test
  void rootBom003EveryMetadataAndNullField() throws Exception {
    for (String key : ACTUAL.keySet()) {
      var changed = new HashMap<>(ACTUAL);
      changed.put(key, "wrong");
      assertThrows(
          IOException.class, () -> RootReleaseAdmission.verifyPlatform(literal(), changed));
      var missing = new HashMap<>(ACTUAL);
      missing.remove(key);
      assertThrows(
          NullPointerException.class,
          () -> RootReleaseAdmission.verifyPlatform(literal(), missing));
    }
    var f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> RootReleaseAdmission.create(f.context, f.expected, null, () -> ACTUAL));
    assertThrows(
        NullPointerException.class,
        () ->
            RootReleaseAdmission.create(
                f.context, f.expected, RootReleaseAdmissionTest::literal, null));
    assertThrows(
        NullPointerException.class,
        () -> RootReleaseAdmission.create(f.context, f.expected, () -> null, () -> ACTUAL));
    assertThrows(
        NullPointerException.class,
        () ->
            RootReleaseAdmission.create(
                f.context, f.expected, RootReleaseAdmissionTest::literal, () -> null));
  }

  @Test
  void rootBom004CloseOrChangedRootCannotMint() throws Exception {
    var f = new Fixture();
    var unknown = new AssertionError("PRIVATE");
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class,
            () ->
                RootReleaseAdmission.create(
                    f.context,
                    f.expected,
                    () -> {
                      throw unknown;
                    },
                    () -> ACTUAL)));
    assertThrows(
        IOException.class,
        () ->
            RootReleaseAdmission.create(
                f.context,
                f.expected,
                () -> {
                  throw new IOException("owner close unavailable");
                },
                () -> ACTUAL));
    assertThrows(
        IOException.class,
        () ->
            RootReleaseAdmission.create(
                f.context,
                f.expected,
                () -> {
                  f.kernel.uid = 1;
                  return literal();
                },
                () -> ACTUAL));
  }

  @Test
  void rootBom005ActorAndSchemaFailureBeforeBegin() throws Exception {
    var f = new Fixture();
    var subject = f.subject();
    assertThrows(
        SQLException.class, () -> subject.verifyMorning(connection(f.events, true), f.expected));
    assertTrue(f.events.contains("rows.close"));
    assertTrue(f.events.contains("statement.close"));
    assertThrows(NullPointerException.class, () -> subject.verifyMorning(null, f.expected));
    assertThrows(
        NullPointerException.class, () -> subject.verifyMorning(connection(f.events, false), null));
    var other =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            f.expected.boot(),
            f.expected.invocation(),
            f.expected.pid(),
            f.expected.startTicks(),
            f.expected.initStartTicks(),
            f.expected.controlGroup());
    assertThrows(
        IOException.class,
        () -> subject.verifyMorning(connection(new ArrayList<>(), false), other));
    var apiKernel = new RootStartupContextTest.Fixture();
    var api = new RootStartupContext(apiKernel);
    var apiExpected = api.capture(RootStartupContext.Service.API);
    var apiSubject =
        RootReleaseAdmission.create(
            api, apiExpected, RootReleaseAdmissionTest::literal, () -> ACTUAL);
    assertThrows(
        IOException.class,
        () -> apiSubject.verifyMorning(connection(new ArrayList<>(), false), apiExpected));
  }

  @Test
  void rootBom006CurrentReloadAndInterruption() throws Exception {
    var f = new Fixture();
    var count = new AtomicInteger();
    var subject =
        RootReleaseAdmission.create(
            f.context,
            f.expected,
            () -> {
              if (count.incrementAndGet() > 1) throw new IOException("changed current");
              return literal();
            },
            () -> ACTUAL);
    var events = new ArrayList<String>();
    assertThrows(
        IOException.class, () -> subject.verifyMorning(connection(events, false), f.expected));
    assertTrue(events.isEmpty());
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> RootReleaseAdmission.verifyPlatform(literal(), ACTUAL));
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void rootBom007FixedOsVectors() throws Exception {
    var actualFile = publicOsDirectory.resolve("public-os-release");
    Files.writeString(actualFile, "ID=ubuntu\nVERSION_ID=26.04\n");
    var nativeIo = new RootReleaseAdmission.NativeOsIo();
    assertEquals(27L, nativeIo.attributes(actualFile).get("size"));
    try (var stream = nativeIo.open(actualFile)) {
      assertArrayEquals(
          "ID=ubuntu\nVERSION_ID=26.04\n".getBytes(java.nio.charset.StandardCharsets.UTF_8),
          stream.readAllBytes());
    }
    var admitted = new OsFixture();
    assertEquals("ID=ubuntu\nVERSION_ID=26.04\n", admitted.read());
    admitted.released();
    // Old held inode stays unchanged; a parent reopen binds to a different current ancestor.
    for (String ancestor : List.of("/usr", "/usr/lib")) {
      var replaced = new OsFixture();
      replaced.changedAncestor = ancestor;
      assertThrows(IOException.class, replaced::read);
      assertEquals(2, replaced.opens.get(ancestor));
      replaced.released();
    }
    for (String key :
        List.of("uid", "gid", "mode", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
      for (String node : List.of("/usr", "/usr/lib", "/usr/lib/os-release")) {
        var invalid = new OsFixture();
        invalid.mutation =
            (name, values) -> {
              if (name.equals(node)) values.remove(key);
            };
        assertThrows(IOException.class, invalid::read, node + key);
        invalid.released();
      }
    }
    for (String node : List.of("/usr", "/usr/lib", "/usr/lib/os-release")) {
      var acl = new OsFixture();
      acl.aclAt = node;
      assertThrows(IOException.class, acl::read);
      acl.released();
    }
    for (String node : List.of("/usr", "/usr/lib/os-release")) {
      for (String key : List.of("uid", "gid", "mode", "nlink", "size", "dev", "ino")) {
        var fixture = new OsFixture();
        fixture.mutation =
            (name, values) -> {
              if (!name.equals(node)) return;
              Object value =
                  switch (key) {
                    case "uid", "gid", "mode" -> 1;
                    case "nlink" -> node.endsWith("os-release") ? 2 : 1;
                    case "size" -> node.endsWith("os-release") ? 0L : -1L;
                    case "dev" -> -1L;
                    default -> 0L;
                  };
              values.put(key, value);
            };
        assertThrows(IOException.class, fixture::read);
        fixture.released();
      }
    }
    var tooLarge = new OsFixture();
    tooLarge.mutation =
        (name, values) -> {
          if (name.endsWith("os-release")) values.put("size", 8193L);
        };
    assertThrows(IOException.class, tooLarge::read);
    tooLarge.released();
    var interrupted = new OsFixture();
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, interrupted::read);
    } finally {
      Thread.interrupted();
    }
    interrupted.released();
    for (String mode :
        List.of(
            "empty",
            "oversize",
            "badUtf8",
            "close",
            "io",
            "null",
            "unknown",
            "changedFile",
            "nullAcl",
            "nonroot",
            "interrupt",
            "lostRoot")) {
      var fixture = new OsFixture();
      fixture.mode = mode;
      Throwable failure = assertThrows(Throwable.class, fixture::read, mode);
      Thread.interrupted();
      if (mode.equals("unknown")) assertSame(fixture.unknown, failure);
      fixture.released();
    }
    for (int position = 1; position <= admitted.operations; position++) {
      var fixture = new OsFixture();
      fixture.failAt = position;
      assertThrows(IOException.class, fixture::read);
      assertEquals(position, fixture.reached);
      fixture.released();
    }
    for (String os :
        List.of(
            "ID=ubuntu\nVERSION_ID=26.04\n", "ID=\"ubuntu\"\nVERSION_ID=\"26.04\"\nNAME=Ubuntu\n"))
      assertEquals(
          ACTUAL, RootReleaseAdmission.platform(os, "x86_64", "25", "PUBLIC VENDOR", "25.0.4"));
    for (String os :
        List.of(
            "",
            "ID=ubuntu\n",
            "VERSION_ID=26.04\n",
            "ID=ubuntu\nID=ubuntu\nVERSION_ID=26.04\n",
            "ID=ubuntu\nVERSION_ID=\"\"\n",
            "ID=ubuntu\nVERSION_ID=\"26.04\n",
            "ID=ubuntu\nVERSION_ID=\"\n",
            "ID=é\nVERSION_ID=26.04\n"))
      assertThrows(
          IOException.class,
          () -> RootReleaseAdmission.platform(os, "x86_64", "25", "PUBLIC VENDOR", "25.0.4"));
    assertThrows(
        NullPointerException.class,
        () -> RootReleaseAdmission.platform(null, "x86_64", "25", "PUBLIC VENDOR", "25.0.4"));
  }

  /** Synthetic fixed-host namespace: retained old handles keep their original inode. */
  static final class OsFixture
      implements DirectoryCalls, InodeSecurityCalls, RootReleaseAdmission.OsIo {
    final Map<Integer, String> held = new HashMap<>();
    final Map<Integer, Long> inodes = new HashMap<>();
    final Map<String, Integer> opens = new HashMap<>();
    final RuntimeException unknown = new IllegalStateException("PUBLIC unknown");
    BiConsumer<String, Map<String, Object>> mutation = (name, values) -> {};
    int next = 10;
    int operations;
    int failAt;
    int reached;
    int streams;
    String changedAncestor = "";
    String aclAt = "";
    String mode = "";
    boolean read;

    void event() throws StorageIoException {
      if (++operations == failAt) {
        reached = operations;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    int handle(String name) throws StorageIoException {
      event();
      int id = next++;
      held.put(id, name);
      int count = opens.merge(name, 1, Integer::sum);
      inodes.put(
          id,
          (long) name.hashCode()
              + Integer.MAX_VALUE
              + (name.equals(changedAncestor) && count > 1 ? 100 : 0));
      return id;
    }

    public int openRoot() throws StorageIoException {
      return handle("");
    }

    public int openDirectory(int parent, String name) throws StorageIoException {
      return handle(held.get(parent) + "/" + name);
    }

    public int openEntry(int parent, String name) throws StorageIoException {
      return handle(held.get(parent) + "/" + name);
    }

    public void close(int id) throws StorageIoException {
      assertNotNull(held.remove(id));
      inodes.remove(id);
      event();
    }

    public int createFile(int parent, String name) {
      throw new AssertionError("read only");
    }

    public void createDirectory(int parent, String name) {
      throw new AssertionError("read only");
    }

    public void publish(int p, String a, String b) {
      throw new AssertionError("read only");
    }

    public void unlink(int p, String a) {
      throw new AssertionError("read only");
    }

    public void sync(int p) {
      throw new AssertionError("read only");
    }

    int id(Path path) {
      return Integer.parseInt(path.getFileName().toString());
    }

    public Map<String, Object> attributes(Path path) throws IOException {
      event();
      String name = held.get(id(path));
      boolean file = name.endsWith("os-release");
      var values =
          new HashMap<String, Object>(
              Map.of(
                  "uid",
                  0,
                  "gid",
                  0,
                  "mode",
                  file ? 0100644 : 040755,
                  "nlink",
                  file ? 1 : 2,
                  "size",
                  file ? 27L : 4096L,
                  "dev",
                  8L,
                  "ino",
                  inodes.get(id(path)),
                  "lastModifiedTime",
                  FileTime.fromMillis(1),
                  "ctime",
                  FileTime.fromMillis(1)));
      if (mode.equals("changedFile") && file && read) values.put("ino", 99L);
      mutation.accept(name, values);
      return values;
    }

    public InputStream open(Path path) throws IOException {
      event();
      if (mode.equals("io")) throw new IOException("PUBLIC IO");
      if (mode.equals("unknown")) throw unknown;
      if (mode.equals("null")) return null;
      byte[] bytes =
          "ID=ubuntu\nVERSION_ID=26.04\n".getBytes(java.nio.charset.StandardCharsets.UTF_8);
      if (mode.equals("empty")) bytes = new byte[0];
      if (mode.equals("oversize")) bytes = new byte[8193];
      if (mode.equals("badUtf8")) {
        bytes = bytes.clone();
        bytes[0] = (byte) 0xff;
      }
      streams++;
      read = true;
      if (mode.equals("interrupt")) Thread.currentThread().interrupt();
      return new ByteArrayInputStream(bytes) {
        public void close() throws IOException {
          streams--;
          event();
          if (mode.equals("close")) throw new IOException("PUBLIC close");
        }
      };
    }

    public byte[] accessAcl(Path path, int max) throws StorageIoException {
      event();
      assertEquals(44, max);
      return mode.equals("nullAcl")
          ? null
          : held.get(id(path)).equals(aclAt) ? new byte[] {1} : new byte[0];
    }

    public boolean readOnlyFilesystem(Path path) {
      throw new AssertionError("OS immutable mount not claimed");
    }

    public long effectiveUid() {
      return mode.equals("nonroot") || (mode.equals("lostRoot") && read) ? 1000 : 0;
    }

    String read() throws IOException {
      return RootReleaseAdmission.readOs(this, this, this);
    }

    void released() {
      assertTrue(held.isEmpty());
      assertEquals(0, streams);
    }
  }

  @Test
  void rootBom008IndependentConcurrentOwners() throws Exception {
    try (var pool = Executors.newFixedThreadPool(4)) {
      var barrier = new CyclicBarrier(4);
      var futures = new ArrayList<Future<Integer>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            pool.submit(
                () -> {
                  var f = new Fixture();
                  barrier.await();
                  var subject = f.subject();
                  subject.verifyMorning(connection(f.events, false), f.expected);
                  return f.loads;
                }));
      for (var f : futures) assertEquals(Integer.valueOf(2), f.get(20, TimeUnit.SECONDS));
    }
  }
}
