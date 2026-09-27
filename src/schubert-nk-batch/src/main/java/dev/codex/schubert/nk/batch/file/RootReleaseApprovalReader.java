package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.ReleaseApproval;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed root approval original in authenticated PID1 host view; no credential catalog extension.
 * The callback finishes all BOM work before return; never exports an inode/path capability.
 * NK-OPS-001/SYS002/004/OPS009/DAT009/UI212/251/253/SS34311.1/SSC096/PG313;
 * PT-OPS-APPROVALREAD001..008. This reader does not publish approval or verify signatures.
 */
@NullMarked
public final class RootReleaseApprovalReader {
  @FunctionalInterface
  public interface Operation<T> {
    T execute(ReleaseApproval approval) throws IOException;
  }

  @FunctionalInterface
  interface Gate {
    void check() throws IOException;
  }

  interface Io {
    Map<String, Object> attributes(Path held) throws IOException;

    SeekableByteChannel open(Path held) throws IOException;
  }

  private final Path etc;
  private final long group;
  private final DirectoryCalls calls;
  private final InodeSecurityCalls security;
  private final Io io;
  private final Gate gate;

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343/SSC096 fixed host /etc approval, PT-OPS-APPROVALREAD008")
  public static RootReleaseApprovalReader create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root snapshot");
    context.recheck(expected);
    return new RootReleaseApprovalReader(
        Path.of("/etc"),
        new FixedServiceIdentity().configurationGroup(),
        LinuxHostDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NativeIo(),
        () -> context.recheck(expected));
  }

  RootReleaseApprovalReader(
      Path etc, long group, DirectoryCalls calls, InodeSecurityCalls security, Io io, Gate gate) {
    this.etc = Objects.requireNonNull(etc, "approval ancestor");
    this.calls = Objects.requireNonNull(calls, "host directory calls");
    this.security = Objects.requireNonNull(security, "approval security");
    this.io = Objects.requireNonNull(io, "approval IO");
    this.gate = Objects.requireNonNull(gate, "root gate");
    if (!etc.isAbsolute()
        || etc.getNameCount() == 0
        || !etc.equals(etc.normalize())
        || group < 1
        || group > 4294967294L) throw new IllegalArgumentException("invalid approval ancestor");
    this.group = group;
  }

  public ReleaseApproval read() throws IOException {
    return execute(value -> value);
  }

  public <T> T execute(Operation<T> operation) throws IOException {
    Objects.requireNonNull(operation, "approval operation");
    check();
    var root = OwnedTransferDirectory.open(calls, etc);
    T result =
        ResourceScope.use(
            root::close,
            () -> {
              var rootBefore = directory(root, 0, 040755);
              var app = root.openExistingChild("schubert-nk");
              return ResourceScope.use(
                  app::close,
                  () -> {
                    var appBefore = directory(app, group, 040750);
                    var approvals = app.openExistingChild("release-approval");
                    T value =
                        ResourceScope.use(
                            approvals::close,
                            () -> {
                              var before = directory(approvals, 0, 040700);
                              require(before.device() == appBefore.device());
                              T answer =
                                  approvals.atExistingEntryHandle(
                                      "current",
                                      held -> {
                                        var fileBefore = inspect(held, false, 0, 0100400);
                                        require(fileBefore.device() == before.device());
                                        ReleaseApproval approval = content(held, fileBefore);
                                        check();
                                        T returned =
                                            Objects.requireNonNull(
                                                operation.execute(approval), "approval result");
                                        check();
                                        require(
                                            fileBefore.equals(inspect(held, false, 0, 0100400)));
                                        approvals.atExistingEntryHandle(
                                            "current",
                                            again -> {
                                              require(
                                                  fileBefore.equals(
                                                      inspect(again, false, 0, 0100400)));
                                              return Boolean.TRUE;
                                            });
                                        return returned;
                                      });
                              require(before.equals(directory(approvals, 0, 040700)));
                              recheck(app, "release-approval", before, 0, 040700);
                              return answer;
                            });
                    require(appBefore.equals(directory(app, group, 040750)));
                    recheck(root, "schubert-nk", appBefore, group, 040750);
                    require(rootBefore.equals(directory(root, 0, 040755)));
                    var again = OwnedTransferDirectory.open(calls, etc);
                    ResourceScope.use(
                        again::close,
                        () -> {
                          require(rootBefore.equals(directory(again, 0, 040755)));
                          return Boolean.TRUE;
                        });
                    return value;
                  });
            });
    check();
    return result;
  }

  private void recheck(
      OwnedTransferDirectory parent,
      String name,
      EnvironmentInodePolicy.Metadata expected,
      long gid,
      int mode)
      throws IOException {
    var reopened = parent.openExistingChild(name);
    ResourceScope.use(
        reopened::close,
        () -> {
          require(expected.equals(directory(reopened, gid, mode)));
          return Boolean.TRUE;
        });
  }

  private ReleaseApproval content(Path held, EnvironmentInodePolicy.Metadata before)
      throws IOException {
    byte[] material = new byte[ReleaseApproval.MAX_BYTES + 1];
    try {
      var channel = Objects.requireNonNull(io.open(held), "approval channel");
      int length =
          ResourceScope.use(
              channel::close,
              () -> {
                require(channel.size() == before.size());
                var buffer = ByteBuffer.wrap(material);
                while (buffer.hasRemaining()) {
                  int position = buffer.position(), remaining = buffer.remaining();
                  int count = channel.read(buffer);
                  if (count == -1) break;
                  require(count > 0 && count <= remaining && buffer.position() == position + count);
                }
                require(buffer.position() == before.size() && channel.size() == before.size());
                return buffer.position();
              });
      require(before.equals(inspect(held, false, 0, 0100400)));
      try {
        return ReleaseApproval.parse(Arrays.copyOf(material, length));
      } catch (IllegalArgumentException malformed) {
        throw EnvironmentInodePolicy.unavailable();
      }
    } finally {
      Arrays.fill(material, (byte) 0);
    }
  }

  private EnvironmentInodePolicy.Metadata directory(
      OwnedTransferDirectory owner, long gid, int mode) throws IOException {
    return owner.atDirectory(held -> inspect(held, true, gid, mode));
  }

  private EnvironmentInodePolicy.Metadata inspect(Path held, boolean directory, long gid, int mode)
      throws IOException {
    var m = EnvironmentInodePolicy.metadata(io.attributes(held));
    require(m.mode() == mode && m.uid() == 0 && m.gid() == gid && m.device() >= 0 && m.inode() > 0);
    require(
        directory
            ? m.links() >= 2 && m.size() >= 0
            : m.links() == 1 && m.size() > 0 && m.size() <= ReleaseApproval.MAX_BYTES);
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0);
    return m;
  }

  private void check() throws IOException {
    require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
    gate.check();
  }

  static final class NativeIo implements Io {
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime");
    }

    public SeekableByteChannel open(Path held) throws IOException {
      return Files.newByteChannel(held, StandardOpenOption.READ);
    }
  }
}
