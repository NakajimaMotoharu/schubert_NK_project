package dev.codex.schubert.nk.bootstrap;

import static dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint.require;
import static dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint.unavailable;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
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

  /** SSC261: resources over the already held entry only; never path/profile authority. */
  interface FileCalls {
    @Nullable FileChannel read(Path held) throws IOException;

    @Nullable FileChannel write(Path held) throws IOException;
  }

  static final FileCalls NATIVE_CHANNELS = new NativeFileCalls();

  private static final class NativeFileCalls implements FileCalls {
    public FileChannel read(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }

    public FileChannel write(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.WRITE);
    }
  }

  @FunctionalInterface
  interface ReadOnlyObservation {
    boolean readOnly() throws IOException;
  }

  /** Scalar pin prerequisite only; real Root inode/full SHA remains caller-owned. */
  static void verifyAgentShape(long size, @Nullable ReadOnlyObservation observation)
      throws IOException {
    if (observation == null) throw new IllegalArgumentException("private PT observation required");
    require(size == 307843 && observation.readOnly());
  }

  private static FileChannel channel(@Nullable FileChannel acquired) {
    if (acquired == null) throw new IllegalArgumentException("private PT channel required");
    return acquired;
  }

  /** PG-D399: data observations only; no startup evidence, configurable path or privilege grant. */
  interface Io {
    InodeSecurityCalls security();

    FixedServiceIdentity resolver();

    OwnedTransferDirectory openRun() throws IOException;

    @Nullable String invocation();

    String cgroup() throws IOException;

    ChildStartupContext.Observed ordinary() throws IOException;

    String filesystem(Path held) throws IOException;

    @Nullable Map<String, ? extends @Nullable Object> attributes(Path held) throws IOException;

    @Nullable Object size(Path held) throws IOException;
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "PG-D399 fixed native run/proc observations; no configurable namespace")
  static final class NativeIo implements Io {
    public InodeSecurityCalls security() {
      return LinuxInodeSecurity.create();
    }

    public FixedServiceIdentity resolver() {
      return new FixedServiceIdentity();
    }

    public OwnedTransferDirectory openRun() throws IOException {
      return OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/run"));
    }

    public @Nullable String invocation() {
      return System.getenv("INVOCATION_ID");
    }

    public String cgroup() throws IOException {
      return Files.readString(Path.of("/proc/self/cgroup"));
    }

    public ChildStartupContext.Observed ordinary() throws IOException {
      return new ChildStartupContext().capture();
    }

    public String filesystem(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }

    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(held, "unix:uid,gid,mode,nlink,dev,ino");
    }

    public Object size(Path held) throws IOException {
      return Files.getAttribute(held, "unix:size");
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC193/PG-D375 fixed Root-managed Linux opt agent pin only; NEXPORT193/native metadata/RO; no arbitrary path or coverage exclusion")
  static void verifyPinnedAgent() throws IOException {
    var security = LinuxInodeSecurity.create();
    Path optPath = Path.of("/opt");
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), optPath),
        OwnedTransferDirectory::close,
        opt -> {
          Identity first = directory(opt, security, 0, 0, 0x41ed);
          ResourceScope.acquire(
              () -> opt.openExistingChild("pgpt-tools-pg390"),
              OwnedTransferDirectory::close,
              tools -> {
                Identity before = directory(tools, security, 0, 0, 0x41ed);
                FileState file =
                    tools.atExistingEntryHandle(
                        "jacoco-agent.jar",
                        held -> {
                          FileState state = file(held, security, 0, 0, 0x81a4);
                          verifyAgentShape(state.size(), () -> security.readOnlyFilesystem(held));
                          require(
                              FixedNativeCoverageProfile.AGENT_SHA256.equals(hash(held, 307843)));
                          require(state.equals(file(held, security, 0, 0, 0x81a4)));
                          return state;
                        });
                tools.atExistingEntryHandle(
                    "jacoco-agent.jar",
                    held -> {
                      require(file.equals(file(held, security, 0, 0, 0x81a4)));
                      return Boolean.TRUE;
                    });
                require(before.equals(directory(tools, security, 0, 0, 0x41ed)));
                return Boolean.TRUE;
              });
          require(first.equals(directory(opt, security, 0, 0, 0x41ed)));
          return Boolean.TRUE;
        });
  }

  static void export(FixedNativeCoverageProfile profile, String name, byte[] bytes)
      throws IOException {
    export(profile, name, bytes, new NativeIo());
  }

  static void export(
      @Nullable FixedNativeCoverageProfile profile,
      @Nullable String name,
      byte @Nullable [] bytes,
      @Nullable Io io)
      throws IOException {
    export(profile, name, bytes, io, NATIVE_CHANNELS);
  }

  static void export(
      @Nullable FixedNativeCoverageProfile profile,
      @Nullable String name,
      byte @Nullable [] bytes,
      @Nullable Io io,
      @Nullable FileCalls channels)
      throws IOException {
    if (profile == null || name == null || bytes == null || io == null || channels == null)
      throw new IllegalArgumentException("private PT export dependencies required");
    // Name is admitted by the closed profile; a second path cannot be substituted by a caller.
    require(
        name.equals(profile.invocation() + ".terminal.exec")
            || (profile.supportsClosing() && name.equals(profile.invocation() + ".closing.exec"))
            || (profile.phase() == FixedNativeCoverageProfile.Phase.ROOT
                && name.equals(profile.invocation() + ".before-exec.exec")));
    var security = io.security();
    var fixed = profile.identity(io.resolver());
    long uid = profile.phase() == FixedNativeCoverageProfile.Phase.ROOT ? 0 : fixed.uid();
    long gid = profile.phase() == FixedNativeCoverageProfile.Phase.ROOT ? 0 : fixed.gid();
    require(security.effectiveUid() == uid);
    require(profile.invocation().equals(io.invocation()));
    String cgroup = profile.cgroup();
    require(cgroup.equals(io.cgroup()));
    var ordinary =
        profile.phase() == FixedNativeCoverageProfile.Phase.ORDINARY
            ? java.util.Optional.of(io.ordinary())
            : java.util.Optional.<ChildStartupContext.Observed>empty();
    if (ordinary.isPresent()) {
      verifyOrdinaryProcess(fixed, ordinary.orElseThrow(), cgroup);
    }
    ResourceScope.acquire(
        io::openRun,
        OwnedTransferDirectory::close,
        run -> {
          Identity top = directory(run, security, 0, 0, 0x41ed, io);
          ResourceScope.acquire(
              () -> run.openExistingChild("schubert-nk"),
              OwnedTransferDirectory::close,
              service -> {
                Identity serviceBefore = directory(service, security, 0, 0, 0x41ed, io);
                ResourceScope.acquire(
                    () -> service.openExistingChild("pt-coverage"),
                    OwnedTransferDirectory::close,
                    parent -> {
                      Identity parentBefore = directory(parent, security, 0, 0, 0x41ed, io);
                      String role = profile.directory();
                      Identity saved =
                          ResourceScope.acquire(
                              () -> parent.openExistingChild(role),
                              OwnedTransferDirectory::close,
                              target -> {
                                Identity original =
                                    directory(target, security, uid, gid, 0x41c0, io);
                                target.atDirectory(
                                    held -> {
                                      require(
                                          "tmpfs".equals(io.filesystem(held))
                                              && !security.readOnlyFilesystem(held));
                                      return Boolean.TRUE;
                                    });
                                write(target, security, uid, gid, name, bytes, io, channels);
                                require(
                                    original.equals(
                                        directory(target, security, uid, gid, 0x41c0, io)));
                                return original;
                              });
                      ResourceScope.acquire(
                          () -> parent.openExistingChild(role),
                          OwnedTransferDirectory::close,
                          reopened -> {
                            require(
                                saved.equals(directory(reopened, security, uid, gid, 0x41c0, io)));
                            return Boolean.TRUE;
                          });
                      require(parentBefore.equals(directory(parent, security, 0, 0, 0x41ed, io)));
                      return Boolean.TRUE;
                    });
                require(serviceBefore.equals(directory(service, security, 0, 0, 0x41ed, io)));
                return Boolean.TRUE;
              });
          require(top.equals(directory(run, security, 0, 0, 0x41ed, io)));
          return Boolean.TRUE;
        });
    require(
        profile.invocation().equals(io.invocation())
            && cgroup.equals(io.cgroup())
            && security.effectiveUid() == uid
            && fixed.equals(profile.identity(io.resolver())));
    if (ordinary.isPresent()) verifySameOrdinaryProcess(ordinary.orElseThrow(), io.ordinary());
  }

  /** PG-D396/NEXPORT598: observed data policy, never startup or namespace authority. */
  static void verifyOrdinaryProcess(
      FixedServiceIdentity.@Nullable Value fixed,
      ChildStartupContext.@Nullable Observed own,
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
      ChildStartupContext.@Nullable Observed before, ChildStartupContext.@Nullable Observed after)
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
    write(directory, security, uid, gid, name, bytes, new NativeIo(), NATIVE_CHANNELS);
  }

  private static void write(
      OwnedTransferDirectory directory,
      InodeSecurityCalls security,
      long uid,
      long gid,
      String name,
      byte[] bytes,
      Io io,
      FileCalls channels)
      throws IOException {
    if (directory == null || security == null || name == null || bytes == null)
      throw new IllegalArgumentException("private PT output dependencies required");
    require(bytes.length >= 5 && bytes.length <= FixedNativeCoverageCheckpoint.MAX_BYTES);
    Identity before = directory(directory, security, uid, gid, 0x41c0, io);
    FileState saved =
        directory.createPrivateEntry(
            name,
            held -> {
              FileState original = file(held, security, uid, gid, 0x8180, io);
              require(original.size() == 0);
              try (var channel = channel(channels.write(held))) {
                require(channel.position() == 0);
                var buffer = ByteBuffer.wrap(bytes);
                while (buffer.hasRemaining()) {
                  int positionBefore = buffer.position();
                  int written = channel.write(buffer);
                  require(
                      written > 0
                          && written == buffer.position() - positionBefore
                          && channel.position() == buffer.position());
                }
                channel.force(true);
                require(channel.size() == bytes.length && channel.position() == bytes.length);
              }
              FileState after = file(held, security, uid, gid, 0x8180, io);
              require(original.identity().equals(after.identity()) && after.size() == bytes.length);
              require(hash(held, bytes.length, channels).equals(digest(bytes)));
              return after;
            });
    // createPrivateEntry has normally closed its owned FD before sync/publication acceptance.
    directory.sync();
    directory.atExistingEntryHandle(
        name,
        held -> {
          require(saved.equals(file(held, security, uid, gid, 0x8180, io)));
          require(hash(held, bytes.length, channels).equals(digest(bytes)));
          return Boolean.TRUE;
        });
    require(before.equals(directory(directory, security, uid, gid, 0x41c0, io)));
  }

  private static Identity directory(
      OwnedTransferDirectory directory, InodeSecurityCalls security, long uid, long gid, int mode)
      throws IOException {
    return directory(directory, security, uid, gid, mode, new NativeIo());
  }

  private static Identity directory(
      OwnedTransferDirectory directory,
      InodeSecurityCalls security,
      long uid,
      long gid,
      int mode,
      Io io)
      throws IOException {
    return directory.atDirectory(
        held -> checked(io.attributes(held), security.accessAcl(held, 44), uid, gid, mode));
  }

  private static FileState file(
      Path held, InodeSecurityCalls security, long uid, long gid, int mode) throws IOException {
    return file(held, security, uid, gid, mode, new NativeIo());
  }

  private static FileState file(
      Path held, InodeSecurityCalls security, long uid, long gid, int mode, Io io)
      throws IOException {
    Identity value = checked(io.attributes(held), security.accessAcl(held, 44), uid, gid, mode);
    Object size = io.size(held);
    if (!(size instanceof Long length) || length < 0) throw unavailable();
    return new FileState(value, length);
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
        device != 0 && inode != 0 && (mode == 0x8180 || mode == 0x81a4 ? links == 1 : links >= 2));
    require(acl.length == 0);
    return new Identity(uid, gid, mode, links, device, inode);
  }

  private static String hash(Path held, int size) throws IOException, NoSuchAlgorithmException {
    return hash(held, size, NATIVE_CHANNELS);
  }

  private static String hash(Path held, int size, FileCalls channels)
      throws IOException, NoSuchAlgorithmException {
    var hash = MessageDigest.getInstance("SHA-256");
    try (var channel = channel(channels.read(held))) {
      require(channel.size() == size && channel.position() == 0);
      var buffer = ByteBuffer.allocate(8192);
      long count = 0;
      while (true) {
        int n = channel.read(buffer);
        if (n < 0) {
          require(n == -1 && buffer.position() == 0 && channel.position() == count);
          break;
        }
        require(n > 0 && n == buffer.position() && n <= size - count);
        count += n;
        require(channel.position() == count);
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
