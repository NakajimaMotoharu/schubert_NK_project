package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.util.Arrays;
import java.util.Objects;
import java.util.Set;
import java.util.function.IntSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Bounded immutable non-secret startup proof in an anonymous Linux memfd, scoped ownership.
 * NK-OPS-001/OPS009; UI212/251; SS341/342/343; SSC086; PT-OPS-SEAL-001..008. Root provenance/inode
 * admission and canonical fresh-binding validation are caller duties. A memfd seal alone is NOT a
 * root/startup authorization. Never place secret bytes here.
 */
@NullMarked
public final class LinuxSealedProof {
  private static final int REQUIRED_SEALS = 15;

  private final CreateCall retainedCreate;
  private final WriteCall write;
  private final ReadCall retainedRead;
  private final FcntlCall fcntl;
  private final ModeCall mode;
  private final CloseCall close;

  public interface CreateCall {
    int call(MemorySegment name, int flags);
  }

  public interface WriteCall {
    long call(int fd, MemorySegment bytes, long count);
  }

  public interface ReadCall {
    long call(int fd, MemorySegment bytes, long count, long offset);
  }

  public interface FcntlCall {
    int call(int fd, int command, int argument);
  }

  public interface ModeCall {
    int call(int fd, int mode);
  }

  public interface CloseCall {
    int call(int fd);
  }

  @FunctionalInterface
  public interface Operation<T> {
    T execute(int borrowedDescriptor) throws IOException;
  }

  public static LinuxSealedProof create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxSealedProof create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("native sealed proof is unavailable");
    return new LinuxSealedProof(
        bind(
            symbols,
            "memfd_create",
            CreateCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.ADDRESS, ValueLayout.JAVA_INT)),
        bind(
            symbols,
            "write",
            WriteCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_LONG,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_LONG)),
        bind(
            symbols,
            "pread",
            ReadCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_LONG,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_LONG,
                ValueLayout.JAVA_LONG)),
        bind(
            symbols,
            "fcntl",
            FcntlCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.firstVariadicArg(2)),
        bind(
            symbols,
            "fchmod",
            ModeCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT)),
        bind(
            symbols,
            "close",
            CloseCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT)));
  }

  LinuxSealedProof(
      CreateCall create,
      WriteCall write,
      ReadCall read,
      FcntlCall fcntl,
      ModeCall mode,
      CloseCall close) {
    this.retainedCreate = Objects.requireNonNull(create, "create");
    this.write = Objects.requireNonNull(write, "write");
    this.retainedRead = Objects.requireNonNull(read, "read");
    this.fcntl = Objects.requireNonNull(fcntl, "fcntl");
    this.mode = Objects.requireNonNull(mode, "mode");
    this.close = Objects.requireNonNull(close, "close");
  }

  /** Caller borrows a reserved CLOEXEC FD only inside the operation; no descriptor may escape. */
  public <T> T withProof(byte[] publicBytes, Operation<T> operation) throws StorageIoException {
    Objects.requireNonNull(publicBytes, "public proof");
    Objects.requireNonNull(operation, "operation");
    if (publicBytes.length == 0 || publicBytes.length > 8192) throw invalid();
    byte[] copy = publicBytes.clone();
    try (Arena arena = Arena.ofConfined()) {
      return ResourceScope.acquire(
          () ->
              new Descriptor(
                  () ->
                      retainedCreate.call(
                          arena.allocateFrom("schubert-startup-proof"),
                          3)), // CLOEXEC|ALLOW_SEALING
          Descriptor::close,
          owned -> prepare(arena, owned.fd, copy, operation));
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  private <T> T prepare(Arena arena, int descriptor, byte[] bytes, Operation<T> operation)
      throws IOException {
    if (mode.call(descriptor, 0x180) != 0) throw unavailable();
    MemorySegment buffer = arena.allocateFrom(ValueLayout.JAVA_BYTE, bytes);
    int offset = 0;
    while (offset < bytes.length) {
      long count = write.call(descriptor, buffer.asSlice(offset), bytes.length - offset);
      if (count <= 0 || count > bytes.length - offset) throw unavailable();
      offset += (int) count;
    }
    // F_SEAL_SEAL|SHRINK|GROW|WRITE; no future mutation or removal of seals.
    if (fcntl.call(descriptor, 1033, REQUIRED_SEALS) != 0) throw unavailable();
    return ResourceScope.acquire(
        () -> new Descriptor(() -> duplicateReserved(descriptor)), // F_DUPFD_CLOEXEC
        Descriptor::close,
        owned -> {
          int reserved = owned.fd;
          if (reserved < 128 || reserved > 65535) throw unavailable();
          return operation.execute(reserved);
        });
  }

  // SS333/BUG2840: the original FD is already owned, not a newly acquired duplicate.
  private int duplicateReserved(int original) {
    int reserved = fcntl.call(original, 1030, 128);
    return reserved == original ? -1 : reserved;
  }

  /**
   * Borrows an already root-admitted FD. Does not adopt/close it or bypass fresh-binding checks.
   */
  public byte[] read(int admittedDescriptor) throws StorageIoException {
    if (admittedDescriptor < 128 || admittedDescriptor > 65535) throw invalid();
    if (fcntl.call(admittedDescriptor, 1034, 0) != REQUIRED_SEALS)
      throw unavailable(); // F_GET_SEALS
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment buffer = arena.allocate(8193);
      int offset = 0;
      while (offset < 8193) {
        long count =
            retainedRead.call(admittedDescriptor, buffer.asSlice(offset), 8193 - offset, offset);
        if (count < 0 || count > 8193 - offset) throw unavailable();
        if (count == 0) {
          if (offset == 0) throw unavailable();
          return buffer.asSlice(0, offset).toArray(ValueLayout.JAVA_BYTE);
        }
        offset += (int) count;
      }
      throw unavailable(); // More than the fixed maximum, including the 8193-byte boundary.
    }
  }

  private void closeOwned(int descriptor) throws StorageIoException {
    if (close.call(descriptor) != 0) throw unavailable(); // Consume once, never retry close.
  }

  private final class Descriptor {
    private final int fd;

    private Descriptor(IntSupplier acquire) throws StorageIoException {
      int acquired = acquire.getAsInt();
      if (acquired < 0) throw unavailable();
      fd = acquired;
    }

    private void close() throws StorageIoException {
      closeOwned(fd);
    }
  }

  @SuppressWarnings("restricted")
  private static <T> T bind(
      SymbolLookup symbols,
      String name,
      Class<T> type,
      FunctionDescriptor signature,
      Linker.Option... options) {
    var address =
        symbols
            .find(name)
            .orElseThrow(() -> new IllegalStateException("native sealed proof is unavailable"));
    return MethodHandleProxies.asInterfaceInstance(
        type, Linker.nativeLinker().downcallHandle(address, signature, options));
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("invalid sealed proof input");
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
