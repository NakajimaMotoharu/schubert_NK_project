package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupProfile;
import dev.codex.schubert.nk.batch.platform.BackupArchiveProcess;
import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Actual parent archives + publication, never owner/receipt authority. SS341/343 SSC110, PG381. */
@NullMarked
final class MorningBackupArtifacts {
  static final List<String> CONFIG =
      List.of(
          "common.yml",
          "api.yml",
          "web.yml",
          "batch.yml",
          "api.env",
          "web.env",
          "backup-profile.json",
          "inbox-inspector.env");
  static final List<String> CREDENTIALS =
      List.of(
          "db-api",
          "db-web",
          "db-batch",
          "db-migration",
          "backup-pgpass",
          "mq-api",
          "mq-web",
          "mq-maintenance",
          "mq-ops",
          "api-context-aes-current",
          "api-inbox-response-aes-current",
          "operation-hmac-current",
          "web-session-aes-current",
          "web-revoke-aes-current",
          "web-log-aes-current",
          "artemis-users",
          "db-inbox-inspector");
  private static final Map<String, String> TOOLS =
      Map.of(
          "pgDumpWrapperSha256",
          "/usr/share/postgresql-common/pg_wrapper",
          "pgRestoreWrapperSha256",
          "/usr/share/postgresql-common/pg_wrapper",
          "pgDumpSha256",
          "/usr/lib/postgresql/18/bin/pg_dump",
          "pgRestoreSha256",
          "/usr/lib/postgresql/18/bin/pg_restore",
          "tarSha256",
          "/usr/bin/tar",
          "ageSha256",
          "/usr/bin/age",
          "artemisArtifactSha256",
          "/opt/apache-artemis-2.56.0/lib/artemis-cli-2.56.0.jar");
  private final RootStartupContext context;
  private final RootStartupContext.Snapshot expected;
  private final MorningParentBudget budget;
  private final InodeSecurityCalls security = LinuxInodeSecurity.create();
  private final DirectoryCalls host = LinuxHostDirectoryCalls.create();
  private final FixedServiceIdentity identities = new FixedServiceIdentity();

  MorningBackupArtifacts(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget) {
    this.context = Objects.requireNonNull(context);
    this.expected = Objects.requireNonNull(expected);
    this.budget = Objects.requireNonNull(budget);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343/SSC110 fixed parent archive/config/tool paths; external VM BARCHIVE acceptance required")
  BackupManifest complete(
      BackupWorkerRequest request,
      MorningDatabaseSession.BackupBegins begins,
      UUID part,
      MorningDatabaseSession.Access database)
      throws IOException {
    check();
    var approval = RootReleaseApprovalReader.create(context, expected);
    var release =
        approval.execute(
            value ->
                StartupReleaseManifest.createHost(identities.configurationGroup()).verify(value));
    var artifact = new java.util.concurrent.atomic.AtomicReference<BackupManifest>();
    Path configPath = Path.of("/etc/schubert-nk");
    ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(host, configPath),
        OwnedTransferDirectory::close,
        config -> {
          var configBefore = directory(config, identities.configurationGroup(), 0x41e8);
          Boolean result =
              config.atExistingEntryHandle(
                  "backup-profile.json",
                  profilePath -> {
                    var profileBefore =
                        file(profilePath, identities.configurationGroup(), 0x81a0, 4096);
                    var profile =
                        BackupProfile.consume(bytes(profilePath, (int) profileBefore.size()));
                    String profileHash = sha(profilePath);
                    require(profile.versions().host().equals(hostname()));
                    require(profile.versions().jdk().equals(System.getProperty("java.version")));
                    require(
                        profileBefore.equals(
                            file(profilePath, identities.configurationGroup(), 0x81a0, 4096)));
                    require(
                        profileHash.equals(
                            release.artifactHashes().get("config/effective/backup-profile.json")));
                    require(
                        profile.versions().app().equals(release.versions().get("app"))
                            && profile.versions().schema().equals(release.versions().get("schema"))
                            && profile
                                .versions()
                                .os()
                                .equals(
                                    release.platform().get("osId")
                                        + "-"
                                        + release.platform().get("osVersion"))
                            && profile.versions().jdk().equals(release.build().get("jdkVersion")));
                    Boolean completed =
                        withTools(
                            profile,
                            0,
                            () ->
                                config.atExistingEntryHandle(
                                    "backup-age-recipient",
                                    recipient -> {
                                      var recipientBefore = file(recipient, 0, 0x8180, 1024);
                                      byte[] publicRecipient =
                                          bytes(recipient, (int) recipientBefore.size());
                                      try {
                                        require(
                                            new String(
                                                    publicRecipient,
                                                    java.nio.charset.StandardCharsets.US_ASCII)
                                                .matches(
                                                    "age1[023456789acdefghjklmnpqrstuvwxyz]{58}\\n"));
                                      } finally {
                                        Arrays.fill(publicRecipient, (byte) 0);
                                      }
                                      String recipientHash = sha(recipient);
                                      require(
                                          recipientHash.equals(
                                              release
                                                  .artifactHashes()
                                                  .get("config/effective/backup-age-recipient")));
                                      Boolean archives =
                                          withInputs(
                                              config,
                                              CONFIG,
                                              0,
                                              false,
                                              () -> {
                                                return ResourceScope
                                                    .<OwnedTransferDirectory, Boolean, IOException>
                                                        acquire(
                                                            () ->
                                                                config.openExistingChild(
                                                                    "credentials"),
                                                            OwnedTransferDirectory::close,
                                                            credentials -> {
                                                              var credentialsBefore =
                                                                  directory(credentials, 0, 0x41c0);
                                                              return withInputs(
                                                                  credentials,
                                                                  CREDENTIALS,
                                                                  0,
                                                                  true,
                                                                  () -> {
                                                                    var identity =
                                                                        identities.resolveBackup();
                                                                    return ResourceScope
                                                                        .<OwnedTransferDirectory,
                                                                            Boolean, IOException>
                                                                            acquire(
                                                                                MorningBackupArtifacts
                                                                                    ::openBackup,
                                                                                OwnedTransferDirectory
                                                                                    ::close,
                                                                                backup -> {
                                                                                  ResourceScope
                                                                                      .<OwnedTransferDirectory,
                                                                                          Boolean,
                                                                                          IOException>
                                                                                          acquire(
                                                                                              () ->
                                                                                                  backup
                                                                                                      .openExistingChild(
                                                                                                          request
                                                                                                                  .directoryName()
                                                                                                              + ".part"),
                                                                                              OwnedTransferDirectory
                                                                                                  ::close,
                                                                                              pending -> {
                                                                                                directory(
                                                                                                    pending,
                                                                                                    identity
                                                                                                        .gid(),
                                                                                                    0x41c0,
                                                                                                    identity
                                                                                                        .uid());
                                                                                                var
                                                                                                    processes =
                                                                                                        new BackupArchiveProcess(
                                                                                                            security,
                                                                                                            budget);
                                                                                                write(
                                                                                                    pending,
                                                                                                    "config.tar",
                                                                                                    output ->
                                                                                                        config
                                                                                                            .atDirectory(
                                                                                                                source -> {
                                                                                                                  processes
                                                                                                                      .configuration(
                                                                                                                          source,
                                                                                                                          output,
                                                                                                                          CONFIG);
                                                                                                                  return Boolean
                                                                                                                      .TRUE;
                                                                                                                }));
                                                                                                write(
                                                                                                    pending,
                                                                                                    "credentials.tar.age",
                                                                                                    output ->
                                                                                                        credentials
                                                                                                            .atDirectory(
                                                                                                                source -> {
                                                                                                                  processes
                                                                                                                      .credentials(
                                                                                                                          source,
                                                                                                                          output,
                                                                                                                          recipient,
                                                                                                                          CREDENTIALS);
                                                                                                                  return Boolean
                                                                                                                      .TRUE;
                                                                                                                }));
                                                                                                return Boolean
                                                                                                    .TRUE;
                                                                                              });
                                                                                  check();
                                                                                  var observed =
                                                                                      new BackupArtifactVerifier(
                                                                                              backup,
                                                                                              security,
                                                                                              identity
                                                                                                  .uid(),
                                                                                              identity
                                                                                                  .gid())
                                                                                          .observePending(
                                                                                              request);
                                                                                  var manifest =
                                                                                      new BackupManifest(
                                                                                          begins
                                                                                              .database(),
                                                                                          begins
                                                                                              .configuration(),
                                                                                          request
                                                                                              .started(),
                                                                                          Instant
                                                                                              .now()
                                                                                              .truncatedTo(
                                                                                                  ChronoUnit
                                                                                                      .MICROS),
                                                                                          profile
                                                                                              .versions(),
                                                                                          recipientHash,
                                                                                          observed
                                                                                              .dump(),
                                                                                          observed
                                                                                              .configuration(),
                                                                                          observed
                                                                                              .credentials());
                                                                                  artifact.set(
                                                                                      manifest); // Claims only: no
                                                                                  // DB or
                                                                                  // publication
                                                                                  // before ALL
                                                                                  // input
                                                                                  // closes.
                                                                                  check();
                                                                                  require(
                                                                                      credentialsBefore
                                                                                          .equals(
                                                                                              directory(
                                                                                                  credentials,
                                                                                                  0,
                                                                                                  0x41c0)));
                                                                                  return Boolean
                                                                                      .TRUE;
                                                                                });
                                                                  });
                                                            });
                                              });
                                      require(
                                          recipientBefore.equals(file(recipient, 0, 0x8180, 1024)));
                                      return archives;
                                    }));
                    require(
                        profileBefore.equals(
                            file(profilePath, identities.configurationGroup(), 0x81a0, 4096)));
                    return completed;
                  });
          require(configBefore.equals(directory(config, identities.configurationGroup(), 0x41e8)));
          return result;
        });
    check();
    var current =
        approval.execute(
            value ->
                StartupReleaseManifest.createHost(identities.configurationGroup()).verify(value));
    require(release.equals(current));
    var manifest = Objects.requireNonNull(artifact.get(), "actual observed backup content");
    var identity = identities.resolveBackup();
    var backupCalls = LinuxDirectoryCalls.create();
    Path backupPath = Path.of("/srv/schubert-nk/backup");
    ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(backupCalls, backupPath),
        OwnedTransferDirectory::close,
        backup -> {
          new BackupManifestPublisher(backup, security, identity.uid(), identity.gid())
              .create(manifest, part);
          new BackupBundlePublisher(backup, security, identity.uid(), identity.gid())
              .publish(manifest);
          database.completeBackup(
              begins,
              new BackupBundleCompletion(backup, security, identity.uid(), identity.gid()),
              manifest.directoryName());
          check();
          return Boolean.TRUE;
        });
    check();
    return manifest;
  }

  @FunctionalInterface
  private interface Work {
    Boolean run() throws IOException;
  }

  @FunctionalInterface
  private interface Writer {
    Boolean write(Path held) throws IOException;
  }

  private Boolean withTools(BackupProfile profile, int index, Work work) throws IOException {
    if (index == BackupProfile.TOOL_KEYS.size()) return work.run();
    String key = BackupProfile.TOOL_KEYS.get(index);
    Path fixed = Path.of(Objects.requireNonNull(TOOLS.get(key)));
    Path parent = Objects.requireNonNull(fixed.getParent());
    return ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(host, parent),
        OwnedTransferDirectory::close,
        root ->
            root.atExistingEntryHandle(
                Objects.requireNonNull(fixed.getFileName(), "fixed tool file name").toString(),
                held -> {
                  var before = tool(held);
                  require(sha(held).equals(profile.toolHashes().get(key)));
                  Boolean result = withTools(profile, index + 1, work);
                  require(before.equals(tool(held)));
                  check();
                  return result;
                }));
  }

  private Boolean withInputs(
      OwnedTransferDirectory directory,
      List<String> names,
      int index,
      boolean credential,
      Work work)
      throws IOException {
    if (index == names.size()) return work.run();
    String name = names.get(index);
    long group =
        credential
            ? 0
            : name.equals("api.env")
                ? identities.resolve(ServiceConfigFiles.Service.API).gid()
                : name.equals("web.env")
                    ? identities.resolve(ServiceConfigFiles.Service.WEB).gid()
                    : identities.configurationGroup();
    int mode = inputMode(name, credential);
    return directory.atExistingEntryHandle(
        name,
        held -> {
          var before = file(held, group, mode, 65536);
          Boolean result = withInputs(directory, names, index + 1, credential, work);
          require(before.equals(file(held, group, mode, 65536)));
          check();
          return result;
        });
  }

  /** SS343 SSC197 / BUG771: static Inspector env is not an API/Web private env. */
  static int inputMode(String name, boolean credential) {
    Objects.requireNonNull(name, "fixed backup input name");
    if (!(credential ? CREDENTIALS : CONFIG).contains(name))
      throw new IllegalArgumentException("backup input name outside fixed catalog");
    return credential || name.equals("api.env") || name.equals("web.env") ? 0x8180 : 0x81a0;
  }

  private void write(OwnedTransferDirectory pending, String name, Writer writer)
      throws IOException {
    UUID temporary = UUID.randomUUID();
    pending.createPrivatePart(
        temporary,
        held -> {
          file(held, 0, 0x8180, 0);
          writer.write(held);
          check();
          try (var channel = FileChannel.open(held, StandardOpenOption.WRITE)) {
            channel.force(true);
          }
          return Boolean.TRUE;
        });
    pending.publishAs(temporary, name);
    pending.sync();
    check();
  }

  private EnvironmentInodePolicy.Metadata directory(
      OwnedTransferDirectory owned, long group, int mode) throws IOException {
    return directory(owned, group, mode, 0);
  }

  private EnvironmentInodePolicy.Metadata directory(
      OwnedTransferDirectory owned, long group, int mode, long uid) throws IOException {
    return owned.atDirectory(
        held -> {
          var m = metadata(held);
          requireDirectoryMetadata(m, group, mode, uid);
          acl(held);
          return m;
        });
  }

  private EnvironmentInodePolicy.Metadata file(Path held, long group, int mode, long maximum)
      throws IOException {
    var m = metadata(held);
    requireFileMetadata(m, group, mode, maximum);
    acl(held);
    return m;
  }

  private EnvironmentInodePolicy.Metadata tool(Path held) throws IOException {
    var m = metadata(held);
    requireToolMetadata(m);
    acl(held);
    return m;
  }

  /** Pure internal value guards, no Root/FD admission and no filesystem repair. */
  static void requireDirectoryMetadata(
      EnvironmentInodePolicy.Metadata m, long group, int mode, long uid) throws IOException {
    Objects.requireNonNull(m);
    require(
        m.mode() == mode && m.uid() == uid && m.gid() == group && m.links() >= 2 && m.size() >= 0);
  }

  static void requireFileMetadata(
      EnvironmentInodePolicy.Metadata m, long group, int mode, long maximum) throws IOException {
    Objects.requireNonNull(m);
    require(
        m.mode() == mode
            && m.uid() == 0
            && m.gid() == group
            && m.links() == 1
            && m.size() >= 0
            && m.size() <= maximum);
  }

  static void requireToolMetadata(EnvironmentInodePolicy.Metadata m) throws IOException {
    Objects.requireNonNull(m);
    require(
        (m.mode() == 0x81a4 || m.mode() == 0x81ed)
            && m.uid() == 0
            && m.gid() == 0
            && m.links() == 1
            && m.size() > 0
            && m.size() <= 268435456L);
  }

  private EnvironmentInodePolicy.Metadata metadata(Path held) throws IOException {
    check();
    return EnvironmentInodePolicy.metadata(
        Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime"));
  }

  private void acl(Path held) throws IOException {
    byte[] acl = security.accessAcl(held, 44);
    requireNoAccessAcl(acl);
    check();
  }

  static void requireNoAccessAcl(@org.jspecify.annotations.Nullable byte[] acl) throws IOException {
    require(acl != null && acl.length == 0);
  }

  private byte[] bytes(Path held, int size) throws IOException {
    byte[] owned = new byte[size];
    try (var input = FileChannel.open(held, StandardOpenOption.READ)) {
      var buffer = ByteBuffer.wrap(owned);
      while (buffer.hasRemaining()) {
        check();
        require(input.read(buffer) > 0);
      }
      require(input.read(ByteBuffer.allocate(1)) == -1 && input.size() == size);
      return owned;
    } catch (IOException | RuntimeException | Error failure) {
      Arrays.fill(owned, (byte) 0);
      throw failure;
    }
  }

  private String sha(Path held) throws IOException {
    try {
      MessageDigest digest = MessageDigest.getInstance("SHA-256");
      byte[] bytes = new byte[65536];
      try (var input = FileChannel.open(held, StandardOpenOption.READ)) {
        long size = input.size();
        long readTotal = 0;
        var buffer = ByteBuffer.wrap(bytes);
        // PG-D804/2476: one read per iteration; EOF still skips the original body.
        while (true) {
          int read = input.read(buffer);
          if (read == -1) break;
          check();
          require(read > 0);
          readTotal += read;
          buffer.flip();
          digest.update(buffer);
          buffer.clear();
        }
        require(readTotal == size && input.size() == size);
        return HexFormat.of().formatHex(digest.digest());
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    } catch (java.security.NoSuchAlgorithmException impossible) {
      throw EnvironmentInodePolicy.unavailable();
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed root-owned backup output namespace")
  private static OwnedTransferDirectory openBackup() throws IOException {
    return OwnedTransferDirectory.open(
        LinuxDirectoryCalls.create(), Path.of("/srv/schubert-nk/backup"));
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC110 actual fixed host hostname, not DNS/caller input")
  private String hostname() throws IOException {
    Path etcPath = Path.of("/etc");
    return ResourceScope.<OwnedTransferDirectory, String, IOException>acquire(
        () -> OwnedTransferDirectory.open(host, etcPath),
        OwnedTransferDirectory::close,
        etc -> {
          var before = directory(etc, 0, 0x41ed);
          String value =
              etc.atExistingEntryHandle(
                  "hostname",
                  held -> {
                    var first = file(held, 0, 0x81a4, 129);
                    byte[] owned = bytes(held, (int) first.size());
                    try {
                      String text = new String(owned, java.nio.charset.StandardCharsets.US_ASCII);
                      require(text.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,127}\\n"));
                      require(first.equals(file(held, 0, 0x81a4, 129)));
                      return text.substring(0, text.length() - 1);
                    } finally {
                      Arrays.fill(owned, (byte) 0);
                    }
                  });
          require(before.equals(directory(etc, 0, 0x41ed)));
          return value;
        });
  }

  private void check() throws IOException {
    budget.requireWithin();
    context.recheck(expected);
    require(security.effectiveUid() == 0);
  }
}
