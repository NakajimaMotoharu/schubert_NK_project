package dev.codex.schubert.nk.bootstrap;

import static dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint.require;
import static dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint.unavailable;

import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC193 fixed isolated-PT namespace. No create/chmod/repair of configured directories, no vendor
 * pathname writer and no existing-file resume. Root operator provisions the four new private role
 * directories before signed deployment. Partial output remains quarantined on every failure.
 * NK-OPS-001 / OPS009,TST004 / UI251 / SS333342343451 / PT-OPS-NEXPORT193001..006.
 */
@NullMarked
final class NativeCoveragePrivateFile {
  private NativeCoveragePrivateFile() {}

  record Identity(long uid, long gid, int mode, int links, long device, long inode) {}

  private record FileState(Identity identity, long size) {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC193/PG-D375 fixed Root-managed Linux opt agent pin only; NEXPORT193/native metadata/RO; no arbitrary path or coverage exclusion")
  static void verifyPinnedAgent() throws IOException {
    var security = LinuxInodeSecurity.create();
    var opt = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/opt"));
    ResourceScope.use(
        opt::close,
        () -> {
          Identity first = directory(opt, security, 0, 0, 040755);
          var tools = opt.openExistingChild("pgpt-tools-pg390");
          ResourceScope.use(
              tools::close,
              () -> {
                Identity before = directory(tools, security, 0, 0, 040755);
                FileState file =
                    tools.atExistingEntryHandle(
                        "jacoco-agent.jar",
                        held -> {
                          FileState state = file(held, security, 0, 0, 0100644);
                          require(state.size() == 307843 && security.readOnlyFilesystem(held));
                          require(
                              FixedNativeCoverageProfile.AGENT_SHA256.equals(hash(held, 307843)));
                          require(state.equals(file(held, security, 0, 0, 0100644)));
                          return state;
                        });
                tools.atExistingEntryHandle(
                    "jacoco-agent.jar",
                    held -> {
                      require(file.equals(file(held, security, 0, 0, 0100644)));
                      return Boolean.TRUE;
                    });
                require(before.equals(directory(tools, security, 0, 0, 040755)));
                return Boolean.TRUE;
              });
          require(first.equals(directory(opt, security, 0, 0, 040755)));
          return Boolean.TRUE;
        });
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC193/PG-D375 fixed Linux run/proc capability and four PT role directories only; NEXPORT193/native; no arbitrary path or coverage exclusion")
  static void export(FixedNativeCoverageProfile profile, String name, byte[] bytes)
      throws IOException {
    // Name is admitted by the closed profile; a second path cannot be substituted by a caller.
    require(
        name.equals(profile.invocation() + ".terminal.exec")
            || (profile.phase() == FixedNativeCoverageProfile.Phase.ROOT
                && name.equals(profile.invocation() + ".before-exec.exec")));
    var security = LinuxInodeSecurity.create();
    var fixed = profile.identity(new FixedServiceIdentity());
    long uid = profile.phase() == FixedNativeCoverageProfile.Phase.ROOT ? 0 : fixed.uid();
    long gid = profile.phase() == FixedNativeCoverageProfile.Phase.ROOT ? 0 : fixed.gid();
    require(security.effectiveUid() == uid);
    require(profile.invocation().equals(System.getenv("INVOCATION_ID")));
    String cgroup = profile.cgroup();
    require(cgroup.equals(Files.readString(Path.of("/proc/self/cgroup"))));
    var ordinary =
        profile.phase() == FixedNativeCoverageProfile.Phase.ORDINARY
            ? java.util.Optional.of(new ChildStartupContext().capture())
            : java.util.Optional.<ChildStartupContext.Observed>empty();
    if (ordinary.isPresent()) {
      verifyOrdinaryProcess(fixed, ordinary.orElseThrow(), cgroup);
    }
    var run = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/run"));
    ResourceScope.use(
        run::close,
        () -> {
          Identity top = directory(run, security, 0, 0, 040755);
          var service = run.openExistingChild("schubert-nk");
          ResourceScope.use(
              service::close,
              () -> {
                Identity serviceBefore = directory(service, security, 0, 0, 040755);
                var parent = service.openExistingChild("pt-coverage");
                ResourceScope.use(
                    parent::close,
                    () -> {
                      Identity parentBefore = directory(parent, security, 0, 0, 040755);
                      String role = profile.directory();
                      var target = parent.openExistingChild(role);
                      Identity saved =
                          ResourceScope.use(
                              target::close,
                              () -> {
                                Identity original = directory(target, security, uid, gid, 040700);
                                target.atDirectory(
                                    held -> {
                                      require(
                                          "tmpfs".equals(Files.getFileStore(held).type())
                                              && !security.readOnlyFilesystem(held));
                                      return Boolean.TRUE;
                                    });
                                write(target, security, uid, gid, name, bytes);
                                require(
                                    original.equals(directory(target, security, uid, gid, 040700)));
                                return original;
                              });
                      var reopened = parent.openExistingChild(role);
                      ResourceScope.use(
                          reopened::close,
                          () -> {
                            require(saved.equals(directory(reopened, security, uid, gid, 040700)));
                            return Boolean.TRUE;
                          });
                      require(parentBefore.equals(directory(parent, security, 0, 0, 040755)));
                      return Boolean.TRUE;
                    });
                require(serviceBefore.equals(directory(service, security, 0, 0, 040755)));
                return Boolean.TRUE;
              });
          require(top.equals(directory(run, security, 0, 0, 040755)));
          return Boolean.TRUE;
        });
    require(
        profile.invocation().equals(System.getenv("INVOCATION_ID"))
            && cgroup.equals(Files.readString(Path.of("/proc/self/cgroup")))
            && security.effectiveUid() == uid
            && fixed.equals(profile.identity(new FixedServiceIdentity())));
    if (ordinary.isPresent())
      verifySameOrdinaryProcess(ordinary.orElseThrow(), new ChildStartupContext().capture());
  }

  /** PG-D396/NEXPORT598: observed data policy, never startup or namespace authority. */
  static void verifyOrdinaryProcess(
      @Nullable FixedServiceIdentity.Value fixed,
      @Nullable ChildStartupContext.Observed own,
      @Nullable String cgroup)
      throws IOException {
    if (fixed == null || own == null || cgroup == null) throw unavailable();
    require(
        own.uid() == fixed.uid()
            && own.gid() == fixed.gid()
            && own.groups().equals(fixed.groups())
            && own.zeroCapabilities()
            && own.noNewPrivileges()
            && own.cgroup().equals(cgroup));
  }

  static void verifySameOrdinaryProcess(
      @Nullable ChildStartupContext.Observed before, @Nullable ChildStartupContext.Observed after)
      throws IOException {
    if (before == null || after == null) throw unavailable();
    require(before.equals(after));
  }

  /** Borrowed directory only; all file callbacks retain the originally created inode descriptor. */
  static void write(
      OwnedTransferDirectory directory,
      InodeSecurityCalls security,
      long uid,
      long gid,
      String name,
      byte[] bytes)
      throws IOException {
    if (directory == null || security == null || name == null || bytes == null)
      throw new IllegalArgumentException("private PT output dependencies required");
    require(bytes.length >= 5 && bytes.length <= FixedNativeCoverageCheckpoint.MAX_BYTES);
    Identity before = directory(directory, security, uid, gid, 040700);
    FileState saved =
        directory.createPrivateEntry(
            name,
            held -> {
              FileState original = file(held, security, uid, gid, 0100600);
              require(original.size() == 0);
              try (var channel = FileChannel.open(held, StandardOpenOption.WRITE)) {
                var buffer = ByteBuffer.wrap(bytes);
                while (buffer.hasRemaining()) require(channel.write(buffer) > 0);
                channel.force(true);
                require(channel.size() == bytes.length);
              }
              FileState after = file(held, security, uid, gid, 0100600);
              require(original.identity().equals(after.identity()) && after.size() == bytes.length);
              require(hash(held, bytes.length).equals(digest(bytes)));
              return after;
            });
    // createPrivateEntry has normally closed its owned FD before sync/publication acceptance.
    directory.sync();
    directory.atExistingEntryHandle(
        name,
        held -> {
          require(saved.equals(file(held, security, uid, gid, 0100600)));
          require(hash(held, bytes.length).equals(digest(bytes)));
          return Boolean.TRUE;
        });
    require(before.equals(directory(directory, security, uid, gid, 040700)));
  }

  private static Identity directory(
      OwnedTransferDirectory directory, InodeSecurityCalls security, long uid, long gid, int mode)
      throws IOException {
    return directory.atDirectory(held -> checked(held, security, uid, gid, mode));
  }

  private static FileState file(
      Path held, InodeSecurityCalls security, long uid, long gid, int mode) throws IOException {
    Identity value = checked(held, security, uid, gid, mode);
    Object size = Files.getAttribute(held, "unix:size");
    if (!(size instanceof Long length) || length < 0) throw unavailable();
    return new FileState(value, length);
  }

  private static Identity checked(
      Path held, InodeSecurityCalls security, long uid, long gid, int mode) throws IOException {
    Map<String, Object> a = Files.readAttributes(held, "unix:uid,gid,mode,nlink,dev,ino");
    return checked(a, security.accessAcl(held, 44), uid, gid, mode);
  }

  /** Independent metadata oracle port; never grants namespace or process authority. */
  static Identity checked(
      @Nullable Map<String, ? extends @Nullable Object> a,
      byte @Nullable [] acl,
      long uid,
      long gid,
      int mode)
      throws IOException {
    if (a == null || acl == null) throw unavailable();
    if (!(a.get("uid") instanceof Integer owner)
        || !(a.get("gid") instanceof Integer group)
        || !(a.get("mode") instanceof Integer permissions)
        || !(a.get("nlink") instanceof Integer links)
        || !(a.get("dev") instanceof Long device)
        || !(a.get("ino") instanceof Long inode)) throw unavailable();
    require(
        Integer.toUnsignedLong(owner) == uid
            && Integer.toUnsignedLong(group) == gid
            && permissions == mode);
    require(
        device != 0
            && inode != 0
            && (mode == 0100600 || mode == 0100644 ? links == 1 : links >= 2));
    require(acl.length == 0);
    return new Identity(uid, gid, mode, links, device, inode);
  }

  private static String hash(Path held, int size) throws IOException, NoSuchAlgorithmException {
    var hash = MessageDigest.getInstance("SHA-256");
    try (var channel = FileChannel.open(held, StandardOpenOption.READ)) {
      require(channel.size() == size);
      var buffer = ByteBuffer.allocate(8192);
      long count = 0;
      while (true) {
        int n = channel.read(buffer);
        if (n < 0) break;
        require(n > 0 && (count += n) <= size);
        buffer.flip();
        hash.update(buffer);
        buffer.clear();
      }
      require(count == size && channel.size() == size);
      return HexFormat.of().formatHex(hash.digest());
    }
  }

  private static String digest(byte[] bytes) throws NoSuchAlgorithmException {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }
}
