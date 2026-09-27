package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.ZipFile;
import org.jspecify.annotations.NullMarked;

/**
 * Independent actual-byte release-manifest digest under caller-held A. Not a BOM verifier or
 * current permit issuer. Only the root-owned current selector may be a symlink; target traversal
 * and manifest are NOFOLLOW. All owners close before the digest is returned. NK-OPS-001;
 * SYS002/004,OPS009; UI251; SS342/343 SSC089; PG300; PT-OPS-RELEASE-001..008.
 */
@NullMarked
public final class StartupReleaseManifest {
  private static final int MAX_BYTES = 1_048_576;
  private final Path opt;
  private final long group;
  private final DirectoryCalls calls;
  private final InodeSecurityCalls security;
  private final Io io;

  interface Io {
    Map<String, Object> attributes(Path held) throws IOException;

    Path selector(Path heldParent) throws IOException;

    SeekableByteChannel open(Path held) throws IOException;

    default DirectoryStream<Path> names(Path held) throws IOException {
      return Files.newDirectoryStream(held);
    }

    default ZipFile archive(Path held) throws IOException {
      return new ZipFile(held.toFile());
    }
  }

  @FunctionalInterface
  private interface ReleaseOperation<T> {
    T read(OwnedTransferDirectory release, String version) throws StorageIoException;
  }

  /** Actual file agreement only, not root approval authority or a complete startup permit. */
  public record Contents(
      String version, String sha256, List<SchemaHistoryAdmission.Row> migrations) {
    public Contents {
      Objects.requireNonNull(version, "release version");
      Objects.requireNonNull(sha256, "manifest digest");
      migrations = List.copyOf(migrations);
    }

    @Override
    public List<SchemaHistoryAdmission.Row> migrations() {
      return List.copyOf(migrations);
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 SSC089 fixed /opt root; PT-OPS-RELEASE-008")
  public static StartupReleaseManifest create(long configurationGroup) {
    return new StartupReleaseManifest(
        Path.of("/opt"),
        configurationGroup,
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo());
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 SSC096 authenticated root caller uses fixed PID1 host /opt view")
  public static StartupReleaseManifest createHost(long configurationGroup) {
    return new StartupReleaseManifest(
        Path.of("/opt"),
        configurationGroup,
        LinuxHostDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo());
  }

  StartupReleaseManifest(
      Path opt, long group, DirectoryCalls calls, InodeSecurityCalls security, Io io) {
    this.opt = Objects.requireNonNull(opt, "release root");
    this.calls = Objects.requireNonNull(calls, "directory calls");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "release IO");
    if (!opt.isAbsolute()
        || opt.getNameCount() == 0
        || !opt.equals(opt.normalize())
        || group < 1
        || group > 4294967294L) throw new IllegalArgumentException("invalid release root");
    this.group = group;
  }

  public String sha256() throws IOException {
    return inspect((release, version) -> manifest(release));
  }

  /** Borrowed claims: caller must keep the independently authenticated approval scope held. */
  public Contents verify(ReleaseApproval approval) throws IOException {
    Objects.requireNonNull(approval, "borrowed release approval");
    return inspect(
        (release, version) ->
            new ReleasePayloadVerification(this, group, io, security)
                .verify(release, version, approval));
  }

  private <T> T inspect(ReleaseOperation<T> operation) throws IOException {
    try {
      var root = OwnedTransferDirectory.open(calls, opt);
      return ResourceScope.use(
          root::close,
          () -> {
            Snapshot top = directory(root, 0, 040755);
            var app = root.openExistingChild("schubert-nk");
            return ResourceScope.use(
                app::close,
                () -> {
                  Snapshot appBefore = directory(app, group, 040750);
                  T digest = selected(app, operation);
                  require(appBefore.equals(directory(app, group, 040750)));
                  var reopened = root.openExistingChild("schubert-nk");
                  ResourceScope.use(
                      reopened::close,
                      () -> {
                        require(appBefore.equals(directory(reopened, group, 040750)));
                        return Boolean.TRUE;
                      });
                  require(top.equals(directory(root, 0, 040755)));
                  var reopenedTop = OwnedTransferDirectory.open(calls, opt);
                  ResourceScope.use(
                      reopenedTop::close,
                      () -> {
                        require(top.equals(directory(reopenedTop, 0, 040755)));
                        return Boolean.TRUE;
                      });
                  return digest;
                });
          });
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  private <T> T selected(OwnedTransferDirectory app, ReleaseOperation<T> operation)
      throws StorageIoException {
    return app.atExistingEntryHandle(
        "current",
        link -> {
          Snapshot before = checked(link, 0, 0120777, 1, -1);
          String version = version(app.atDirectory(io::selector), opt);
          var releases = app.openExistingChild("releases");
          T result =
              ResourceScope.use(
                  releases::close,
                  () -> {
                    Snapshot releasesBefore = directory(releases, group, 040750);
                    var release = releases.openExistingChild(version);
                    return ResourceScope.use(
                        release::close,
                        () -> {
                          Snapshot releaseBefore = directory(release, group, 040750);
                          T digest = operation.read(release, version);
                          require(releaseBefore.equals(directory(release, group, 040750)));
                          var reopened = releases.openExistingChild(version);
                          ResourceScope.use(
                              reopened::close,
                              () -> {
                                require(releaseBefore.equals(directory(reopened, group, 040750)));
                                return Boolean.TRUE;
                              });
                          require(releasesBefore.equals(directory(releases, group, 040750)));
                          var reopenedReleases = app.openExistingChild("releases");
                          ResourceScope.use(
                              reopenedReleases::close,
                              () -> {
                                require(
                                    releasesBefore.equals(
                                        directory(reopenedReleases, group, 040750)));
                                return Boolean.TRUE;
                              });
                          return digest;
                        });
                  });
          require(before.equals(checked(link, 0, 0120777, 1, -1)));
          require(version.equals(version(app.atDirectory(io::selector), opt)));
          app.atExistingEntryHandle(
              "current",
              reopened -> {
                require(before.equals(checked(reopened, 0, 0120777, 1, -1)));
                return Boolean.TRUE;
              });
          return result;
        });
  }

  private String manifest(OwnedTransferDirectory release) throws StorageIoException {
    return release.atExistingEntryHandle(
        "RELEASE-MANIFEST.json",
        held -> {
          Snapshot before = checked(held, group, 0100640, 1, MAX_BYTES);
          MessageDigest hash = MessageDigest.getInstance("SHA-256");
          var channel = Objects.requireNonNull(io.open(held), "manifest channel");
          String digest =
              ResourceScope.use(
                  channel::close,
                  () -> {
                    require(channel.size() == before.size());
                    ByteBuffer buffer = ByteBuffer.allocate(8192);
                    long total = 0;
                    while (true) {
                      int count = channel.read(buffer);
                      if (count < 0) break;
                      require(count > 0);
                      total += count;
                      require(total <= MAX_BYTES);
                      buffer.flip();
                      hash.update(buffer);
                      buffer.clear();
                    }
                    require(total == before.size() && channel.size() == before.size());
                    require(before.equals(checked(held, group, 0100640, 1, MAX_BYTES)));
                    return HexFormat.of().formatHex(hash.digest());
                  });
          release.atExistingEntryHandle(
              "RELEASE-MANIFEST.json",
              reopened -> {
                require(before.equals(checked(reopened, group, 0100640, 1, MAX_BYTES)));
                return Boolean.TRUE;
              });
          return digest;
        });
  }

  private Snapshot directory(OwnedTransferDirectory held, long gid, int mode)
      throws StorageIoException {
    return held.atDirectory(path -> checked(path, gid, mode, 2, -1));
  }

  Snapshot checked(Path path, long gid, int mode, int minimumLinks, long maximum)
      throws IOException {
    Map<String, Object> a = Objects.requireNonNull(io.attributes(path), "inode attributes");
    if (!(a.get("uid") instanceof Integer uid)
        || !(a.get("gid") instanceof Integer actualGroup)
        || !(a.get("mode") instanceof Integer actualMode)
        || !(a.get("nlink") instanceof Integer links)
        || !(a.get("dev") instanceof Long device)
        || !(a.get("ino") instanceof Long inode)
        || !(a.get("size") instanceof Long size)
        || !(a.get("lastModifiedTime") instanceof FileTime modified)
        || !(a.get("ctime") instanceof FileTime changed)) throw unavailable();
    require(uid == 0 && Integer.toUnsignedLong(actualGroup) == gid && actualMode == mode);
    require(links >= minimumLinks && (minimumLinks != 1 || links == 1));
    require(device != 0 && inode != 0 && size >= 0);
    if (maximum >= 0) require(size > 0 && size <= maximum);
    require(Objects.requireNonNull(security.accessAcl(path, 44), "inode ACL").length == 0);
    return new Snapshot(
        uid, actualGroup, actualMode, links, device, inode, size, modified, changed);
  }

  static String version(Path target, Path opt) throws IOException {
    Objects.requireNonNull(target, "release selector");
    Path releases = opt.resolve("schubert-nk/releases");
    require(
        target.isAbsolute()
            && target.equals(target.normalize())
            && releases.equals(target.getParent()));
    String version = Objects.requireNonNull(target.getFileName(), "release version").toString();
    require(version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,63}"));
    return version;
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("release manifest unavailable");
  }

  record Snapshot(
      int uid,
      int gid,
      int mode,
      int links,
      long device,
      long inode,
      long size,
      FileTime modified,
      FileTime changed) {}

  static final class NioIo implements Io {
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(
          held, "unix:uid,gid,mode,nlink,dev,ino,size,lastModifiedTime,ctime");
    }

    public Path selector(Path heldParent) throws IOException {
      return Files.readSymbolicLink(heldParent.resolve("current"));
    }

    public SeekableByteChannel open(Path held) throws IOException {
      return Files.newByteChannel(held, Set.of(StandardOpenOption.READ));
    }
  }
}
