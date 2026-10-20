package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/** Fixed Ubuntu amd64 trusted payloads; held ELF is not a third inherited FD. SSC137/PT297. */
@NullMarked
final class RootServiceExecutableAdmission {
  private static final int RETAINED_SYMBOLIC_LINK_MODE = 0xa1ff;

  private static final java.lang.String LITERAL_JAVA = "java";

  static final String SETPRIV = "86965a019d37dc11d176ce8cbe9f5f5f8f37027c95e03cb4a8cad4c73d940993";
  static final String JAVA = "c324471f8b7933a3cb401eafbc35a7055443779b438a3ab928bda3867a1b8ab1";
  static final String TARGET = "/opt/jdk-25.0.4/bin/java";
  private static final int MAXIMUM = 8 * 1024 * 1024;

  @FunctionalInterface
  interface Work {
    void execute(Path borrowedElf) throws IOException;
  }

  @FunctionalInterface
  interface Capability {
    void requireAbsent(Path held) throws IOException;
  }

  /** SSC306/PT-ROOTELF-SSC306-001..004: internal failure port, never external configuration. */
  @FunctionalInterface
  interface DigestFactory {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  /** SSC308/PT-ROOTGUARD-004: new wrapper before primitive open, no post-open boxing/state. */
  static final class RootDescriptor implements java.io.Closeable {
    private final DirectoryCalls calls;
    final int descriptor;

    RootDescriptor(DirectoryCalls calls) throws StorageIoException {
      this.calls = Objects.requireNonNull(calls);
      int held = this.calls.openRoot();
      if (held < 0) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      descriptor = held;
    }

    @Override
    public void close() throws StorageIoException {
      calls.close(descriptor);
    }
  }

  private RootServiceExecutableAdmission() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 fixed setpriv and unique Java chain, no configurable executable")
  static void withSetpriv(RootStartupContext root, RootStartupContext.Snapshot self, Work work)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(self);
    Objects.requireNonNull(work);
    require(
        self.service() == RootStartupContext.Service.API
            || self.service() == RootStartupContext.Service.WEB);
    root.recheck(self);
    var calls = LinuxDirectoryCalls.create();
    var security = LinuxInodeSecurity.create();
    ResourceScope.acquire(
        () -> new RootDescriptor(calls),
        RootDescriptor::close,
        top -> {
          checked(Path.of("/proc/self/fd/" + top.descriptor), 0x41ed, security);
          return Boolean.TRUE;
        });
    Path usrPath = Path.of("/usr");
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(calls, usrPath),
        OwnedTransferDirectory::close,
        usr -> {
          var beforeUsr = usr.atDirectory(p -> checked(p, 0x41ed, security));
          ResourceScope.acquire(
              () -> usr.openExistingChild("bin"),
              OwnedTransferDirectory::close,
              bin -> {
                var beforeBin = bin.atDirectory(p -> checked(p, 0x41ed, security));
                bin.atExistingEntryHandle(
                    "setpriv",
                    held -> {
                      var admitted =
                          admit(held, SETPRIV, security, security::requireNoFileCapabilities);
                      verifyJava(bin, security);
                      require(admitted.equals(checked(held, 0x81ed, security)));
                      bin.atExistingEntryHandle(
                          "setpriv",
                          fresh -> {
                            require(admitted.equals(checked(fresh, 0x81ed, security)));
                            security.requireNoFileCapabilities(fresh);
                            return Boolean.TRUE;
                          });
                      require(beforeBin.equals(bin.atDirectory(p -> checked(p, 0x41ed, security))));
                      require(beforeUsr.equals(usr.atDirectory(p -> checked(p, 0x41ed, security))));
                      // Every observer must close normally before the kernel can replace this JVM.
                      bin.close();
                      usr.close();
                      root.recheck(self);
                      work.execute(held);
                      return Boolean.TRUE;
                    });
                return Boolean.TRUE;
              });
          return Boolean.TRUE;
        });
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 sole admitted Java link and fixed JDK target")
  private static void verifyJava(OwnedTransferDirectory bin, LinuxInodeSecurity security)
      throws IOException {
    Path target = Path.of(TARGET);
    Path firstTarget = Path.of("/etc/alternatives/java");
    Path etcPath = Path.of("/etc");
    Path optPath = Path.of("/opt");
    bin.atExistingEntryHandle(
        LITERAL_JAVA,
        link -> {
          var before = checked(link, 0xa1ff, security);
          requireSelector(bin, before, firstTarget, security);
          ResourceScope.acquire(
              () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), etcPath),
              OwnedTransferDirectory::close,
              etc -> {
                var etcBefore = etc.atDirectory(p -> checked(p, 0x41ed, security));
                ResourceScope.acquire(
                    () -> etc.openExistingChild("alternatives"),
                    OwnedTransferDirectory::close,
                    alternatives -> {
                      var alternativesBefore =
                          alternatives.atDirectory(p -> checked(p, 0x41ed, security));
                      alternatives.atExistingEntryHandle(
                          LITERAL_JAVA,
                          alternative -> {
                            var alternateBefore = checked(alternative, 0xa1ff, security);
                            requireSelector(alternatives, alternateBefore, target, security);
                            ResourceScope.acquire(
                                () ->
                                    OwnedTransferDirectory.open(
                                        LinuxDirectoryCalls.create(), optPath),
                                OwnedTransferDirectory::close,
                                opt -> {
                                  var optBefore =
                                      opt.atDirectory(p -> checked(p, 0x41ed, security));
                                  ResourceScope.acquire(
                                      () -> opt.openExistingChild("jdk-25.0.4"),
                                      OwnedTransferDirectory::close,
                                      jdk -> {
                                        var jdkBefore =
                                            jdk.atDirectory(p -> checked(p, 0x41ed, security));
                                        ResourceScope.acquire(
                                            () -> jdk.openExistingChild("bin"),
                                            OwnedTransferDirectory::close,
                                            javaBin -> {
                                              var binBefore =
                                                  javaBin.atDirectory(
                                                      p -> checked(p, 0x41ed, security));
                                              javaBin.atExistingEntryHandle(
                                                  LITERAL_JAVA,
                                                  held -> {
                                                    var admitted =
                                                        admit(
                                                            held,
                                                            JAVA,
                                                            security,
                                                            security::requireNoFileCapabilities);
                                                    javaBin.atExistingEntryHandle(
                                                        LITERAL_JAVA,
                                                        reopened -> {
                                                          require(
                                                              admitted.equals(
                                                                  checked(
                                                                      reopened, 0x81ed, security)));
                                                          return Boolean.TRUE;
                                                        });
                                                    return Boolean.TRUE;
                                                  });
                                              require(
                                                  binBefore.equals(
                                                      javaBin.atDirectory(
                                                          p -> checked(p, 0x41ed, security))));
                                              return Boolean.TRUE;
                                            });
                                        require(
                                            jdkBefore.equals(
                                                jdk.atDirectory(
                                                    p -> checked(p, 0x41ed, security))));
                                        return Boolean.TRUE;
                                      });
                                  require(
                                      optBefore.equals(
                                          opt.atDirectory(p -> checked(p, 0x41ed, security))));
                                  return Boolean.TRUE;
                                });
                            require(alternateBefore.equals(checked(alternative, 0xa1ff, security)));
                            requireSelector(alternatives, alternateBefore, target, security);
                            alternatives.atExistingEntryHandle(
                                LITERAL_JAVA,
                                reopened -> {
                                  require(
                                      alternateBefore.equals(checked(reopened, 0xa1ff, security)));
                                  return Boolean.TRUE;
                                });
                            return Boolean.TRUE;
                          });
                      require(
                          alternativesBefore.equals(
                              alternatives.atDirectory(p -> checked(p, 0x41ed, security))));
                      return Boolean.TRUE;
                    });
                require(etcBefore.equals(etc.atDirectory(p -> checked(p, 0x41ed, security))));
                return Boolean.TRUE;
              });
          require(before.equals(checked(link, 0xa1ff, security)));
          requireSelector(bin, before, firstTarget, security);
          bin.atExistingEntryHandle(
              LITERAL_JAVA,
              reopened -> {
                require(before.equals(checked(reopened, 0xa1ff, security)));
                return Boolean.TRUE;
              });
          return Boolean.TRUE;
        });
  }

  /** SSC143: same fixed named Java link and retained link inode; no arbitrary chain. */
  private static void requireSelector(
      OwnedTransferDirectory parent,
      Map<String, Object> held,
      Path expected,
      InodeSecurityCalls security)
      throws IOException {
    parent.atDirectory(
        p -> {
          Path name = p.resolve(LITERAL_JAVA);
          var named =
              Files.readAttributes(
                  name,
                  "unix:uid,gid,mode,nlink,dev,ino,size,lastModifiedTime,ctime",
                  LinkOption.NOFOLLOW_LINKS);
          require(held.equals(checkedAttributes(name, 0xa1ff, named, security)));
          requireSelectorTarget(expected, Files.readSymbolicLink(name));
          return Boolean.TRUE;
        });
  }

  static void requireSelectorTarget(Path expected, Path actual) throws IOException {
    Objects.requireNonNull(expected);
    Objects.requireNonNull(actual);
    require(expected.equals(actual));
  }

  static Map<String, Object> checked(Path held, int mode, InodeSecurityCalls security)
      throws IOException {
    var a =
        Files.readAttributes(held, "unix:uid,gid,mode,nlink,dev,ino,size,lastModifiedTime,ctime");
    return checkedAttributes(held, mode, a, security);
  }

  static Map<String, Object> checkedAttributes(
      Path held, int mode, Map<String, Object> a, InodeSecurityCalls security) throws IOException {
    Objects.requireNonNull(held);
    Objects.requireNonNull(a);
    Objects.requireNonNull(security);
    require(
        a.get("uid") instanceof Integer uid
            && uid == 0
            && a.get("gid") instanceof Integer gid
            && gid == 0
            && a.get("mode") instanceof Integer actualMode
            && actualMode == mode);
    require(a.get("nlink") instanceof Integer links && (mode == 0x41ed ? links >= 2 : links == 1));
    require(
        a.get("dev") instanceof Long dev
            && dev != 0
            && a.get("ino") instanceof Long ino
            && ino != 0);
    require(
        a.get("size") instanceof Long size
            && size >= 0
            && (mode != 0x81ed || size > 0 && size <= MAXIMUM));
    require(a.get("lastModifiedTime") instanceof FileTime && a.get("ctime") instanceof FileTime);
    // On a retained symlink getxattr would follow its target; check its typed metadata instead.
    if (mode != RETAINED_SYMBOLIC_LINK_MODE) require(security.accessAcl(held, 44).length == 0);
    return Map.copyOf(a);
  }

  static Map<String, Object> admit(
      Path held, String expected, InodeSecurityCalls security, Capability capabilities)
      throws IOException {
    Objects.requireNonNull(held);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(security);
    Objects.requireNonNull(capabilities);
    var before = checked(held, 0x81ed, security);
    capabilities.requireAbsent(held);
    String actual =
        ResourceScope.acquire(
            () -> Files.newByteChannel(held, Set.of(StandardOpenOption.READ)),
            SeekableByteChannel::close,
            input -> {
              String result = digest(input);
              require(Long.valueOf(input.size()).equals(before.get("size")));
              return result;
            });
    require(expected.equals(actual) && before.equals(checked(held, 0x81ed, security)));
    capabilities.requireAbsent(held);
    return before;
  }

  static String digest(SeekableByteChannel input) throws IOException {
    Objects.requireNonNull(input);
    return digest(input, () -> MessageDigest.getInstance("SHA-256"));
  }

  /** SSC306: borrowed channel, fixed native binding above; no provider/global mutation. */
  static String digest(SeekableByteChannel input, DigestFactory factory) throws IOException {
    Objects.requireNonNull(input);
    Objects.requireNonNull(factory);
    MessageDigest hash;
    try {
      hash = Objects.requireNonNull(factory.create());
    } catch (NoSuchAlgorithmException known) {
      throw new IOException("root executable unavailable");
    }
    byte[] material = new byte[8192];
    long total = 0;
    try {
      var bytes = ByteBuffer.wrap(material);
      byte[] header = new byte[64];
      while (true) {
        int n = input.read(bytes);
        if (n == -1) {
          require(bytes.position() == 0);
          break;
        }
        // ByteBuffer.position <= capacity == material.length, so equality also proves the bound.
        require(n > 0 && n == bytes.position());
        for (int i = 0; i < n && total + i < header.length; i++)
          header[(int) total + i] = material[i];
        total += n;
        require(total <= MAXIMUM);
        hash.update(material, 0, n);
        bytes.clear();
      }
      require(total >= 64 && total == input.size());
      require(
          header[0] == 127
              && header[1] == 'E'
              && header[2] == 'L'
              && header[3] == 'F'
              && header[4] == 2
              && header[5] == 1
              && header[6] == 1
              && header[18] == 62
              && header[19] == 0);
      return HexFormat.of().formatHex(hash.digest());
    } finally {
      Arrays.fill(material, (byte) 0);
    }
  }
}
