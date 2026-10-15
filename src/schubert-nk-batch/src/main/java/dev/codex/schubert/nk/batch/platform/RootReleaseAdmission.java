package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfig;
import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.batch.file.RootReleaseApprovalReader;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageRootLayout;
import dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed root-only release/schema admission. Public claims/rows/booleans cannot mint this type.
 * Always re-reads the current approval/BOM before schema use; never publishes approval, caches a
 * digest, or substitutes for continuous M/A, terminal units or INVALID. NK-OPS-001/NK-BAT-001;
 * SYS002/004/OPS009/DAT009/UI212/251/253/SS3439.1/11.1/SSC095096/PG-D314/018156;
 * PT-OPS-ROOTBOM001..009.
 */
@NullMarked
public final class RootReleaseAdmission {
  @FunctionalInterface
  interface Loader {
    StartupReleaseManifest.Contents read() throws IOException;
  }

  @FunctionalInterface
  interface Platform {
    Map<String, String> observe() throws IOException;
  }

  interface OsIo {
    Map<String, Object> attributes(Path held) throws IOException;

    InputStream open(Path held) throws IOException;
  }

  private final RootStartupContext context;
  private final RootStartupContext.Snapshot expected;
  private final Loader loader;
  private final Platform platform;

  private RootReleaseAdmission(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      Loader loader,
      Platform platform) {
    this.context = context;
    this.expected = expected;
    this.loader = loader;
    this.platform = platform;
  }

  /** No arbitrary expected digest, approval, reader, path, key or permission flag is accepted. */
  public static RootReleaseAdmission create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root snapshot");
    context.recheck(expected);
    Loader loader =
        () ->
            RootReleaseApprovalReader.create(context, expected)
                .execute(
                    approval ->
                        StartupReleaseManifest.createHost(
                                new FixedServiceIdentity().configurationGroup())
                            .verify(approval));
    return create(context, expected, loader, RootReleaseAdmission::nativePlatform);
  }

  // Package-only ports permit independent policy/ordering PT, never native/root acceptance.
  static RootReleaseAdmission create(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      Loader loader,
      Platform platform)
      throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root snapshot");
    Objects.requireNonNull(loader, "fixed release loader");
    Objects.requireNonNull(platform, "runtime platform");
    context.recheck(expected);
    verifyPlatform(
        Objects.requireNonNull(loader.read(), "closed release result"),
        Objects.requireNonNull(platform.observe(), "runtime platform result"));
    // The loader's approval callback, namespace rechecks and ALL owner closes have finished.
    context.recheck(expected);
    return new RootReleaseAdmission(context, expected, loader, platform);
  }

  /** Borrowed fixed-role connection; refuses stale/wrong actor before any schema query. */
  public void verifyMorning(Connection connection, RootStartupContext.Snapshot caller)
      throws SQLException, IOException {
    verifyFor(connection, caller, RootStartupContext.Service.MORNING);
  }

  /** Actual approved payload observations, freshly bound to the same Morning owner/schema. */
  public StartupReleaseManifest.Contents inspectMorning(
      Connection connection, RootStartupContext.Snapshot caller) throws SQLException, IOException {
    return verifyFor(connection, caller, RootStartupContext.Service.MORNING).contents();
  }

  /** SSC129: freshly verified manifest, actual DB rows and independent runtime observations. */
  public record DatabaseInspection(
      StartupReleaseManifest.Contents contents,
      List<SchemaHistoryAdmission.Row> schemaRows,
      Map<String, String> runtime) {
    public DatabaseInspection {
      Objects.requireNonNull(contents);
      schemaRows = List.copyOf(schemaRows);
      runtime = Map.copyOf(runtime);
    }

    @Override
    public String toString() {
      return "ReleaseDatabaseInspection[actual=<redacted>]";
    }
  }

  public DatabaseInspection inspectMorningDatabase(
      Connection connection, RootStartupContext.Snapshot caller) throws SQLException, IOException {
    return verifyFor(connection, caller, RootStartupContext.Service.MORNING);
  }

  /** SSC137: an independently admitted fixed app-role connection, not Morning's advisory owner. */
  public DatabaseInspection inspectServiceDatabase(
      Connection connection, RootStartupContext.Snapshot caller) throws SQLException, IOException {
    Objects.requireNonNull(caller);
    require(
        caller.service() == RootStartupContext.Service.API
            || caller.service() == RootStartupContext.Service.WEB);
    return verifyFor(connection, caller, caller.service());
  }

  /** Non-secret data only; effective parser result is not release/root/permit authority. SSC126. */
  public record EffectiveConfigurations(
      String apiSha256,
      String webSha256,
      StorageRootLayout roots,
      ServiceConfigFiles.Contents apiYaml,
      ServiceConfigFiles.Contents webYaml) {
    public EffectiveConfigurations {
      Objects.requireNonNull(apiSha256);
      Objects.requireNonNull(webSha256);
      Objects.requireNonNull(roots);
      Objects.requireNonNull(apiYaml);
      Objects.requireNonNull(webYaml);
    }

    @Override
    public String toString() {
      return "EffectiveConfigurations[non-secret=<redacted>]";
    }
  }

  public EffectiveConfigurations inspectConfigurations() throws IOException {
    return inspectConfigurations(ServiceConfigFiles.production());
  }

  /** Package port for independent fixed YAML vectors, not a native root admission factory. */
  EffectiveConfigurations inspectConfigurations(NonSecretConfigSource source) throws IOException {
    Objects.requireNonNull(source, "actual non-secret fixed YAML reader");
    require(expected.service() == RootStartupContext.Service.MORNING);
    return readConfigurations(source);
  }

  public EffectiveConfigurations inspectServiceConfigurations() throws IOException {
    return inspectServiceConfigurations(ServiceConfigFiles.production());
  }

  EffectiveConfigurations inspectServiceConfigurations(NonSecretConfigSource source)
      throws IOException {
    Objects.requireNonNull(source);
    require(
        expected.service() == RootStartupContext.Service.API
            || expected.service() == RootStartupContext.Service.WEB);
    return readConfigurations(source);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC126/137 fixed four deployment roots, shared strict parser unchanged")
  private EffectiveConfigurations readConfigurations(NonSecretConfigSource source)
      throws IOException {
    context.recheck(expected);
    var apiYaml = Objects.requireNonNull(source.read(ServiceConfigFiles.Service.API));
    var webYaml = Objects.requireNonNull(source.read(ServiceConfigFiles.Service.WEB));
    require(apiYaml.commonYaml().equals(webYaml.commonYaml()));
    EffectiveConfigurations observed;
    try {
      var api = ApiNonSecretConfig.parse(apiYaml.commonYaml(), apiYaml.serviceYaml());
      var web = WebNonSecretConfig.parse(webYaml.commonYaml(), webYaml.serviceYaml());
      require(
          api.value("nk.api.storage.asset-root").equals(web.value("nk.web.storage.asset-root"))
              && api.value("nk.api.storage.transfer-root")
                  .equals(web.value("nk.web.storage.transfer-root")));
      observed =
          new EffectiveConfigurations(
              api.canonicalSha256(),
              web.canonicalSha256(),
              new StorageRootLayout(
                  Path.of(api.value("nk.api.storage.asset-root")),
                  Path.of(api.value("nk.api.storage.transfer-root")),
                  Path.of("/srv/schubert-nk/backup"),
                  Path.of("/var/log/schubert-nk"),
                  Path.of("/var/lib/schubert-nk/artemis"),
                  Path.of("/srv/schubert-nk/staging")),
              apiYaml,
              webYaml);
    } catch (IllegalArgumentException | java.security.NoSuchAlgorithmException invalid) {
      throw new IOException("root effective configuration unavailable");
    }
    context.recheck(expected);
    return observed;
  }

  public void recheckConfigurations(EffectiveConfigurations observed) throws IOException {
    recheckConfigurations(observed, ServiceConfigFiles.production());
  }

  public void recheckServiceConfigurations(EffectiveConfigurations observed) throws IOException {
    Objects.requireNonNull(observed);
    require(observed.equals(inspectServiceConfigurations()));
    context.recheck(expected);
  }

  void recheckConfigurations(EffectiveConfigurations observed, NonSecretConfigSource source)
      throws IOException {
    Objects.requireNonNull(observed);
    require(observed.equals(inspectConfigurations(source)));
    context.recheck(expected);
  }

  /** Cleanup child verifies its own fixed root actor and fresh release/schema, not the parent's. */
  public void verifyCleanup(Connection connection, RootStartupContext.Snapshot caller)
      throws SQLException, IOException {
    verifyFor(connection, caller, RootStartupContext.Service.CLEANUP);
  }

  public void verifyExpiry(Connection connection, RootStartupContext.Snapshot caller)
      throws SQLException, IOException {
    verifyFor(connection, caller, RootStartupContext.Service.EXPIRY);
  }

  private DatabaseInspection verifyFor(
      Connection connection, RootStartupContext.Snapshot caller, RootStartupContext.Service service)
      throws SQLException, IOException {
    Objects.requireNonNull(connection, "admitted root connection");
    Objects.requireNonNull(caller, "root context");
    require(expected.equals(caller) && caller.service() == service);
    context.recheck(expected);
    var current = Objects.requireNonNull(loader.read(), "closed current release result");
    var actualRuntime = Objects.requireNonNull(platform.observe(), "runtime platform result");
    verifyPlatform(current, actualRuntime);
    var actualRows = new SchemaHistoryAdmission(current.migrations()).inspect(connection);
    context.recheck(expected);
    return new DatabaseInspection(current, actualRows, actualRuntime);
  }

  static void verifyPlatform(StartupReleaseManifest.Contents release, Map<String, String> actual)
      throws IOException {
    require(!Thread.currentThread().isInterrupted());
    for (String key : List.of("osId", "osVersion", "architecture", "javaFeature"))
      require(
          Objects.requireNonNull(release.platform().get(key), "release platform field")
              .equals(Objects.requireNonNull(actual.get(key), "runtime platform field")));
    for (String key : List.of("jdkVendor", "jdkVersion"))
      require(
          Objects.requireNonNull(release.build().get(key), "release JDK field")
              .equals(Objects.requireNonNull(actual.get(key), "runtime JDK field")));
  }

  private static Map<String, String> nativePlatform() throws IOException {
    String os =
        readOs(LinuxHostDirectoryCalls.create(), LinuxInodeSecurity.create(), new NativeOsIo());
    return platform(
        os,
        Objects.requireNonNull(System.getProperty("os.arch")),
        Integer.toString(Runtime.version().feature()),
        Objects.requireNonNull(System.getProperty("java.vendor")),
        Objects.requireNonNull(System.getProperty("java.version")));
  }

  // Fixed purpose package ports, not a public root authority or configurable OS filename.
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed host /usr/lib/os-release, no argv/config path; ROOTBOM007")
  static String readOs(DirectoryCalls calls, InodeSecurityCalls security, OsIo io)
      throws IOException {
    Objects.requireNonNull(calls);
    Objects.requireNonNull(security);
    Objects.requireNonNull(io);
    require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
    Path fixedUsr = Path.of("/usr");
    var usr = OwnedTransferDirectory.open(calls, fixedUsr);
    String result =
        ResourceScope.use(
            usr::close,
            () -> {
              var first = usr.atDirectory(p -> osSnapshot(p, true, security, io));
              var lib = usr.openExistingChild("lib");
              String text =
                  ResourceScope.use(
                      lib::close,
                      () -> {
                        var before = lib.atDirectory(p -> osSnapshot(p, true, security, io));
                        String value =
                            lib.atExistingEntryHandle(
                                "os-release",
                                held -> {
                                  var file = osSnapshot(held, false, security, io);
                                  var stream =
                                      Objects.requireNonNull(io.open(held), "owned OS stream");
                                  byte[] bytes =
                                      ResourceScope.use(
                                          stream::close, () -> stream.readNBytes(8193));
                                  require(Long.valueOf(bytes.length).equals(file.get("size")));
                                  require(file.equals(osSnapshot(held, false, security, io)));
                                  lib.atExistingEntryHandle(
                                      "os-release",
                                      again -> {
                                        require(
                                            file.equals(osSnapshot(again, false, security, io)));
                                        return Boolean.TRUE;
                                      });
                                  return StandardCharsets.UTF_8
                                      .newDecoder()
                                      .decode(ByteBuffer.wrap(bytes))
                                      .toString();
                                });
                        require(
                            before.equals(lib.atDirectory(p -> osSnapshot(p, true, security, io))));
                        var reopened = usr.openExistingChild("lib");
                        ResourceScope.use(
                            reopened::close,
                            () -> {
                              require(
                                  before.equals(
                                      reopened.atDirectory(
                                          p -> osSnapshot(p, true, security, io))));
                              return Boolean.TRUE;
                            });
                        return value;
                      });
              require(first.equals(usr.atDirectory(p -> osSnapshot(p, true, security, io))));
              var current = OwnedTransferDirectory.open(calls, fixedUsr);
              ResourceScope.use(
                  current::close,
                  () -> {
                    require(
                        first.equals(current.atDirectory(p -> osSnapshot(p, true, security, io))));
                    return Boolean.TRUE;
                  });
              return text;
            });
    require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
    return result;
  }

  private static Map<String, Object> osSnapshot(
      Path held, boolean directory, InodeSecurityCalls security, OsIo io) throws IOException {
    var m = Objects.requireNonNull(io.attributes(held), "OS inode metadata");
    require(
        Integer.valueOf(0).equals(m.get("uid"))
            && Integer.valueOf(0).equals(m.get("gid"))
            && Integer.valueOf(directory ? 040755 : 0100644).equals(m.get("mode")));
    require(m.get("nlink") instanceof Integer links && (directory ? links >= 2 : links == 1));
    require(
        m.get("size") instanceof Long size && (directory ? size >= 0 : size > 0 && size <= 8192));
    require(
        m.get("dev") instanceof Long device
            && device >= 0
            && m.get("ino") instanceof Long inode
            && inode > 0);
    require(m.get("lastModifiedTime") instanceof FileTime && m.get("ctime") instanceof FileTime);
    require(Objects.requireNonNull(security.accessAcl(held, 44), "OS ACL").length == 0);
    return Map.copyOf(m);
  }

  static final class NativeOsIo implements OsIo {
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:uid,gid,mode,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    public InputStream open(Path held) throws IOException {
      return Files.newInputStream(held);
    }
  }

  static Map<String, String> platform(
      String os, String architecture, String feature, String vendor, String version)
      throws IOException {
    var result = new HashMap<String, String>();
    for (String line : Objects.requireNonNull(os, "OS release").split("\n", -1)) {
      for (String key : List.of("ID", "VERSION_ID")) {
        if (line.startsWith(key + "=")) {
          String value = line.substring(key.length() + 1);
          if (value.startsWith("\"") && value.endsWith("\"") && value.length() > 1)
            value = value.substring(1, value.length() - 1);
          require(value.matches("[a-z0-9._-]{1,128}") && result.put(key, value) == null);
        }
      }
    }
    require(result.size() == 2);
    return Map.of(
        "osId",
        Objects.requireNonNull(result.get("ID")),
        "osVersion",
        Objects.requireNonNull(result.get("VERSION_ID")),
        "architecture",
        Objects.requireNonNull(architecture),
        "javaFeature",
        Objects.requireNonNull(feature),
        "jdkVendor",
        Objects.requireNonNull(vendor),
        "jdkVersion",
        Objects.requireNonNull(version));
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw new IOException("root release admission unavailable");
  }
}
