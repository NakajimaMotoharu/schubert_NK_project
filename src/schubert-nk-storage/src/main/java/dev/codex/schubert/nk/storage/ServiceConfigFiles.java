package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.UserPrincipal;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed-name, held-inode read of non-secret common and service YAML. It never creates, repairs or
 * logs a config file. OS account membership, ACL/filesystem policy, env location, credential
 * distribution, cross-file atomic rollout and process readiness are separate caller gates.
 * NK-OPS-001; RD SYS-002/004; UI243/253; SS311/342/343 §2/4; PG275/PT-OPS-CFGFILE-001..007.
 */
@NullMarked
public final class ServiceConfigFiles {
  private static final Path PRODUCTION_ROOT = Path.of("/etc/schubert-nk");
  private static final int MAX_BYTES = 16_384;

  interface Io {
    Map<String, Object> attributes(Path heldPath) throws IOException;

    SeekableByteChannel openReadOnly(Path heldPath) throws IOException;
  }

  private static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path heldPath) throws IOException {
      return Files.readAttributes(heldPath, "unix:owner,group,mode,nlink,dev,ino,size,ctime");
    }

    @Override
    public SeekableByteChannel openReadOnly(Path heldPath) throws IOException {
      return Files.newByteChannel(heldPath, Set.of(StandardOpenOption.READ));
    }
  }

  public enum Service {
    API("api.yml"),
    WEB("web.yml");

    private final String fileName;

    Service(String fileName) {
      this.fileName = fileName;
    }
  }

  public record Contents(String commonYaml, String serviceYaml) {
    public Contents {
      Objects.requireNonNull(commonYaml, "common YAML");
      Objects.requireNonNull(serviceYaml, "service YAML");
    }
  }

  private ServiceConfigFiles() {}

  public static Contents read(Service service) throws StorageIoException {
    return read(
        PRODUCTION_ROOT,
        new StorageIdentity("root", "schubert"),
        LinuxDirectoryCalls.create(),
        service);
  }

  static Contents read(Path root, StorageIdentity identity, DirectoryCalls calls, Service service)
      throws StorageIoException {
    return read(root, identity, calls, new NioIo(), service);
  }

  static Contents read(
      Path root, StorageIdentity identity, DirectoryCalls calls, Io io, Service service)
      throws StorageIoException {
    Objects.requireNonNull(root, "config root");
    Objects.requireNonNull(identity, "config identity");
    Objects.requireNonNull(calls, "directory calls");
    Objects.requireNonNull(io, "config IO");
    Objects.requireNonNull(service, "service");
    try {
      OwnedTransferDirectory held = OwnedTransferDirectory.open(calls, root);
      return ResourceScope.use(
          held::close,
          () -> {
            Snapshot before = inspect(held, identity, io);
            String common = readOne(held, "common.yml", identity, before.device(), io);
            String specific = readOne(held, service.fileName, identity, before.device(), io);
            if (!before.equals(inspect(held, identity, io))) throw unavailable();
            return new Contents(common, specific);
          });
    } catch (StorageIoException failure) {
      throw unavailable();
    }
  }

  private static Snapshot inspect(OwnedTransferDirectory held, StorageIdentity identity, Io io)
      throws StorageIoException {
    return held.atDirectory(path -> checked(io.attributes(path), identity, true, -1));
  }

  private static String readOne(
      OwnedTransferDirectory held, String fileName, StorageIdentity identity, long device, Io io)
      throws StorageIoException {
    return held.atExistingEntryHandle(
        fileName,
        path -> {
          Snapshot before = checked(io.attributes(path), identity, false, device);
          SeekableByteChannel channel = io.openReadOnly(path);
          return ResourceScope.use(
              channel::close,
              () -> {
                if (channel.size() != before.size()) throw unavailable();
                ByteBuffer bytes = ByteBuffer.allocate(MAX_BYTES + 1);
                while (true) {
                  int count = channel.read(bytes);
                  if (count < 0) break;
                  if (count == 0 || bytes.position() > MAX_BYTES) throw unavailable();
                }
                if (bytes.position() != before.size() || channel.size() != before.size())
                  throw unavailable();
                Snapshot after = checked(io.attributes(path), identity, false, device);
                if (!before.equals(after)) throw unavailable();
                bytes.flip();
                try {
                  return StandardCharsets.UTF_8
                      .newDecoder()
                      .onMalformedInput(CodingErrorAction.REPORT)
                      .onUnmappableCharacter(CodingErrorAction.REPORT)
                      .decode(bytes)
                      .toString();
                } catch (CharacterCodingException failure) {
                  throw unavailable();
                }
              });
        });
  }

  static Snapshot checked(
      Map<String, Object> attributes,
      StorageIdentity identity,
      boolean directory,
      long expectedDevice)
      throws StorageIoException {
    Objects.requireNonNull(attributes, "inode attributes");
    Objects.requireNonNull(identity, "config identity");
    if (!(attributes.get("owner") instanceof UserPrincipal owner)
        || !(attributes.get("group") instanceof GroupPrincipal group)
        || !(attributes.get("mode") instanceof Integer mode)
        || !(attributes.get("nlink") instanceof Integer links)
        || !(attributes.get("dev") instanceof Long device)
        || !(attributes.get("ino") instanceof Long inode)
        || !(attributes.get("size") instanceof Long size)
        || !(attributes.get("ctime") instanceof FileTime changed)
        || !identity.owner().equals(owner.getName())
        || !identity.group().equals(group.getName())
        || !Integer.valueOf(directory ? 040750 : 0100640).equals(mode)
        || links < 1
        || (!directory && links != 1)
        || device < 0
        || inode < 1
        || size < 0
        || (!directory && (size < 1 || size > MAX_BYTES))
        || (expectedDevice >= 0 && device != expectedDevice)) throw unavailable();
    return new Snapshot(device, inode, mode, links, size, changed);
  }

  record Snapshot(long device, long inode, int mode, int links, long size, FileTime changed) {}

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
