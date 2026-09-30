package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.format.DateTimeFormatterBuilder;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Same Morning callback's actual six roots, SS343 6.17/SSC126, ISSROOT001..003. Read-only paired
 * host/private NOFOLLOW handles; no provisioning, permit or authority fallback.
 */
@NullMarked
final class MorningStartupRoots {
  private static final List<String> IDS =
      List.of("ASSET", "TRANSFER", "BACKUP", "LOG", "ARTEMIS", "STAGING");

  @FunctionalInterface
  interface Gate {
    void check() throws IOException;
  }

  @FunctionalInterface
  interface Profiles {
    List<Profile> read() throws IOException;
  }

  record Profile(long uid, long gid, int mode) {
    Profile {
      if (uid < 0
          || uid > 4294967294L
          || gid < 1
          || gid > 4294967294L
          || (mode != 0750 && mode != 0700))
        throw new IllegalArgumentException("fixed root profile");
    }
  }

  private record Entry(
      String id,
      Path path,
      long device,
      long inode,
      long uid,
      long gid,
      int mode,
      String filesystem) {}

  static final class Observation {
    private final List<Entry> entries;

    private Observation(List<Entry> entries) {
      this.entries = List.copyOf(entries);
    }

    byte[] canonical(StartupPermitRecords.Epoch epoch) throws IOException {
      Objects.requireNonNull(epoch);
      require(epoch.state() == StartupPermitRecords.State.INVALID);
      var activation = epoch.activation();
      var time = new DateTimeFormatterBuilder().appendInstant(6).toFormatter();
      var text =
          new StringBuilder("NKROOTS1\n")
              .append("boot_id=")
              .append(epoch.boot())
              .append('\n')
              .append("epoch_id=")
              .append(epoch.epoch())
              .append('\n')
              .append("run_id=")
              .append(activation.run().id())
              .append('\n')
              .append("cutoff_utc=")
              .append(time.format(activation.run().cutoff()))
              .append('\n')
              .append("activation_id=")
              .append(activation.id())
              .append('\n');
      for (var entry : entries)
        text.append(entry.id())
            .append('|')
            .append(entry.path())
            .append('|')
            .append(entry.device())
            .append('|')
            .append(entry.inode())
            .append('|')
            .append(entry.uid())
            .append('|')
            .append(entry.gid())
            .append('|')
            .append(String.format(Locale.ROOT, "%04o", entry.mode()))
            .append('|')
            .append(entry.filesystem())
            .append("|0|empty\n");
      require(text.length() <= 65536);
      return text.toString().getBytes(StandardCharsets.US_ASCII);
    }

    String sha256(StartupPermitRecords.Epoch epoch) throws IOException {
      byte[] actual = canonical(epoch);
      try {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual));
      } catch (NoSuchAlgorithmException failure) {
        throw new IOException("root digest unavailable");
      } finally {
        Arrays.fill(actual, (byte) 0);
      }
    }

    @Override
    public String toString() {
      return "MorningRootObservation[redacted]";
    }
  }

  private final Gate gate;
  private final List<Path> paths;
  private final Profiles profiles;
  private final DirectoryCalls host;
  private final DirectoryCalls local;
  private final EnvironmentInodePolicy policy;

  static MorningStartupRoots create(
      RootStartupContext context, RootStartupContext.Snapshot expected, StorageRootLayout layout)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    require(expected.service() == RootStartupContext.Service.MORNING);
    context.recheck(expected);
    return new MorningStartupRoots(
        () -> context.recheck(expected),
        layout,
        MorningStartupRoots::nativeProfiles,
        LinuxHostDirectoryCalls.create(),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new InspectorEnvironmentReader.NioIo());
  }

  // Package test ports: no public synthetic factory and no root/permit capability.
  MorningStartupRoots(
      Gate gate,
      StorageRootLayout layout,
      Profiles profiles,
      DirectoryCalls host,
      DirectoryCalls local,
      InodeSecurityCalls security,
      EnvironmentInodePolicy.Source source) {
    this.gate = Objects.requireNonNull(gate);
    Objects.requireNonNull(layout);
    paths =
        List.of(
            layout.asset(),
            layout.transfer(),
            layout.backup(),
            layout.log(),
            layout.artemis(),
            layout.staging());
    this.profiles = Objects.requireNonNull(profiles);
    this.host = Objects.requireNonNull(host);
    this.local = Objects.requireNonNull(local);
    policy =
        new EnvironmentInodePolicy(
            Objects.requireNonNull(security), Objects.requireNonNull(source));
  }

  Observation capture() throws IOException {
    gate.check();
    var fixed = List.copyOf(profiles.read());
    require(fixed.size() == IDS.size());
    var entries = new ArrayList<Entry>();
    var identities = new HashSet<List<Long>>();
    for (int index = 0; index < paths.size(); index++) {
      Path path = paths.get(index);
      String value = path.toString();
      require(value.chars().allMatch(c -> c >= 33 && c <= 126 && c != '|'));
      gate.check();
      var admitted = inspect(path, fixed.get(index));
      require(identities.add(List.of(admitted.metadata().device(), admitted.metadata().inode())));
      entries.add(
          new Entry(
              IDS.get(index),
              path,
              admitted.metadata().device(),
              admitted.metadata().inode(),
              admitted.metadata().uid(),
              admitted.metadata().gid(),
              admitted.metadata().mode() & 07777,
              admitted.filesystem()));
      gate.check();
    }
    require(fixed.equals(List.copyOf(profiles.read())));
    gate.check();
    return new Observation(entries);
  }

  void recheck(Observation original) throws IOException {
    Objects.requireNonNull(original);
    require(original.entries.equals(capture().entries));
    gate.check();
  }

  private EnvironmentInodePolicy.Snapshot inspect(Path path, Profile profile) throws IOException {
    var hostRoot = OwnedTransferDirectory.open(host, path);
    return ResourceScope.use(
        hostRoot::close,
        () -> {
          var localRoot = OwnedTransferDirectory.open(local, path);
          return ResourceScope.use(
              localRoot::close,
              () -> {
                var before = snapshot(hostRoot, profile, true);
                var privateBefore = snapshot(localRoot, profile, false);
                require(
                    before.metadata().equals(privateBefore.metadata())
                        && before.filesystem().equals(privateBefore.filesystem()));
                var hostAgain = OwnedTransferDirectory.open(host, path);
                ResourceScope.use(
                    hostAgain::close,
                    () -> {
                      require(before.equals(snapshot(hostAgain, profile, true)));
                      return true;
                    });
                var localAgain = OwnedTransferDirectory.open(local, path);
                ResourceScope.use(
                    localAgain::close,
                    () -> {
                      require(privateBefore.equals(snapshot(localAgain, profile, false)));
                      return true;
                    });
                require(
                    before.equals(snapshot(hostRoot, profile, true))
                        && privateBefore.equals(snapshot(localRoot, profile, false)));
                return before;
              });
        });
  }

  private EnvironmentInodePolicy.Snapshot snapshot(
      OwnedTransferDirectory directory, Profile profile, boolean hostView) throws IOException {
    return directory.atDirectory(
        p -> policy.roleDirectory(p, profile.uid(), profile.gid(), profile.mode(), hostView));
  }

  private static List<Profile> nativeProfiles() throws IOException {
    var fixed = new FixedServiceIdentity();
    var data = fixed.resolveDataOwner();
    var api = fixed.resolve(ServiceConfigFiles.Service.API);
    var web = fixed.resolve(ServiceConfigFiles.Service.WEB);
    var backup = fixed.resolveBackup();
    var artemis = fixed.resolveArtemis();
    var migration = fixed.resolveMigration();
    return List.of(
        new Profile(data.uid(), fixed.dataReadGroup(), 0750),
        new Profile(api.uid(), web.gid(), 0750),
        new Profile(backup.uid(), backup.gid(), 0700),
        new Profile(0, fixed.configurationGroup(), 0750),
        new Profile(artemis.uid(), artemis.gid(), 0700),
        new Profile(migration.uid(), migration.gid(), 0700));
  }
}
