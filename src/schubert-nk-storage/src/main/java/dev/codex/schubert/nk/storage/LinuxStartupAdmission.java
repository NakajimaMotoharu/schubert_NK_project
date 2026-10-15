package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Child-only admission/ownership of the two inherited A/public-proof descriptors. Native root
 * metadata/seals/read-only A are necessary but not sufficient: caller must additionally admit the
 * canonical fresh context and every mandatory gate before business resources. NK-OPS-001;
 * SYS002/004,OPS009; UI212/251; SS342/343 SSC086/087; PG297; PT-OPS-CHILDFD-001..008.
 */
@NullMarked
public final class LinuxStartupAdmission {
  interface Io {
    int fcntl(int fd, int command, int argument);

    int close(int fd);

    @Nullable Map<String, Object> attributes(int fd) throws IOException;

    byte[] proof(int fd) throws IOException;
  }

  public record Identity(int descriptor, long device, long inode) {}

  /** Trusted child releases A once only after readiness or after all failed business cleanup. */
  public static final class Lease implements AutoCloseable {
    private final Identity retainedIdentity;
    private final FdOwner owner;

    private Lease(Identity identity, FdOwner owner) {
      this.retainedIdentity = identity;
      this.owner = owner;
    }

    public Identity identity() {
      return retainedIdentity;
    }

    @Override
    public void close() throws StorageIoException {
      owner.close();
    }
  }

  @FunctionalInterface
  public interface Operation<T> {
    T execute(Lease admission, byte[] borrowedPublicProof) throws IOException;
  }

  private final Io io;

  LinuxStartupAdmission(Io io) {
    this.io = Objects.requireNonNull(io, "child descriptor IO");
  }

  public static LinuxStartupAdmission create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name")),
        Objects.requireNonNull(System.getProperty("os.arch")),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxStartupAdmission create(String os, String arch, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(arch, "architecture");
    Objects.requireNonNull(symbols, "native symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(arch))
      throw unsupported();
    var fcntl =
        bind(
            symbols,
            "fcntl",
            LinuxExecDescriptors.FcntlCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.firstVariadicArg(2));
    var close =
        bind(
            symbols,
            "close",
            LinuxSealedProof.CloseCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT));
    return new LinuxStartupAdmission(new NativeIo(fcntl, close, LinuxSealedProof.create()));
  }

  @SuppressWarnings("restricted")
  private static <T> T bind(
      SymbolLookup symbols,
      String name,
      Class<T> type,
      FunctionDescriptor descriptor,
      Linker.Option... options) {
    return MethodHandleProxies.asInterfaceInstance(
        type,
        Linker.nativeLinker()
            .downcallHandle(
                symbols.find(name).orElseThrow(LinuxStartupAdmission::unsupported),
                descriptor,
                options));
  }

  private static IllegalStateException unsupported() {
    return new IllegalStateException("native startup admission unavailable");
  }

  public <T> T withAdmitted(int admissionFd, int proofFd, Operation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "child startup operation");
    if (admissionFd < 128
        || admissionFd > 65535
        || proofFd < 128
        || proofFd > 65535
        || admissionFd == proofFd)
      throw new IllegalArgumentException("invalid child startup descriptors");
    var admissionOwner = new FdOwner(admissionFd, io);
    return ResourceScope.use(
        admissionOwner::close,
        () -> {
          byte[][] payload = {new byte[0]};
          try {
            Identity identity =
                ResourceScope.use(
                    new FdOwner(proofFd, io)::close,
                    () -> {
                      // Both are newly inherited (CLOEXEC0). No future process may inherit either
                      // capability.
                      require(io.fcntl(admissionFd, 1, 0) == 0 && io.fcntl(proofFd, 1, 0) == 0);
                      require(io.fcntl(admissionFd, 2, 1) == 0 && io.fcntl(proofFd, 2, 1) == 0);
                      Attributes proof = attributes(proofFd);
                      require(proof.links() == 0 && proof.size() > 0 && proof.size() <= 8192);
                      require(io.fcntl(proofFd, 1034, 0) == 15);
                      Attributes admission = attributes(admissionFd);
                      require(admission.links() == 1 && admission.size() == 0);
                      int flags = io.fcntl(admissionFd, 3, 0);
                      require(flags == 0 || flags == 32768); // O_RDONLY, optional O_LARGEFILE only
                      payload[0] = Objects.requireNonNull(io.proof(proofFd), "public proof bytes");
                      require(payload[0].length == proof.size());
                      return new Identity(admissionFd, admission.device(), admission.inode());
                    });
            // Proof owner is consumed before callback; A owner is outermost and consumed last.
            return operation.execute(new Lease(identity, admissionOwner), payload[0]);
          } finally {
            Arrays.fill(payload[0], (byte) 0);
          }
        });
  }

  private Attributes attributes(int fd) throws IOException {
    Map<String, Object> m = io.attributes(fd);
    if (m == null
        || !(m.get("mode") instanceof Integer mode)
        || !(m.get("uid") instanceof Integer uid)
        || !(m.get("gid") instanceof Integer gid)
        || !(m.get("nlink") instanceof Integer links)
        || !(m.get("size") instanceof Long size)
        || !(m.get("dev") instanceof Long device)
        || !(m.get("ino") instanceof Long inode)) throw unavailable();
    require(mode == 0x8180 && uid == 0 && gid == 0 && device != 0 && inode != 0);
    return new Attributes(links, size, device, inode);
  }

  private record Attributes(int links, long size, long device, long inode) {}

  private static void require(boolean valid) throws StorageIoException {
    if (!valid) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private static final class FdOwner {
    private final int fd;
    private final Io io;
    private final AtomicBoolean consumed = new AtomicBoolean();

    FdOwner(int fd, Io io) {
      this.fd = fd;
      this.io = io;
    }

    void close() throws StorageIoException {
      if (consumed.compareAndSet(false, true) && io.close(fd) != 0) throw unavailable();
    }
  }

  static final class NativeIo implements Io {
    private final LinuxExecDescriptors.FcntlCall retainedFcntl;
    private final LinuxSealedProof.CloseCall retainedClose;
    private final LinuxSealedProof reader;

    NativeIo(
        LinuxExecDescriptors.FcntlCall fcntl,
        LinuxSealedProof.CloseCall close,
        LinuxSealedProof reader) {
      this.retainedFcntl = Objects.requireNonNull(fcntl);
      this.retainedClose = Objects.requireNonNull(close);
      this.reader = Objects.requireNonNull(reader);
    }

    public int fcntl(int fd, int command, int argument) {
      return retainedFcntl.call(fd, command, argument);
    }

    public int close(int fd) {
      return retainedClose.call(fd);
    }

    public Map<String, Object> attributes(int fd) throws IOException {
      return Files.readAttributes(
          Path.of("/proc/self/fd/" + fd), "unix:mode,uid,gid,nlink,size,dev,ino");
    }

    public byte[] proof(int fd) throws IOException {
      return reader.read(fd);
    }
  }
}
