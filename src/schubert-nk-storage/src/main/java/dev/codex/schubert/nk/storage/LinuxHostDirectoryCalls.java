package dev.codex.schubert.nk.storage;

import java.lang.foreign.*;
import java.lang.invoke.MethodHandleProxies;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Root startup inspector's read-only host mount view, no setns or sandbox change.
 * NK-OPS-001/OPS009; UI212/251; SS341/342/343; SSC087; PT-OPS-HOST-001..008. The caller first
 * authenticates PID1/system manager, boot and kernel proc provenance, then uses
 * OwnedTransferDirectory for every subsequent NOFOLLOW segment/inode. This native SPI does not
 * attest provenance/permission or issue a startup authorization on its own. All host capabilities
 * must close before exec, never pass to an ordinary service.
 */
@NullMarked
public final class LinuxHostDirectoryCalls implements DirectoryCalls {
  private final DirectoryCalls children;
  private final InodeSecurityCalls security;
  private final OpenCall open;

  public interface OpenCall {
    int call(MemorySegment path, int flags, int mode);
  }

  public static LinuxHostDirectoryCalls create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  @SuppressWarnings("restricted")
  static LinuxHostDirectoryCalls create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("native host inspection is unavailable");
    var address =
        symbols
            .find("open")
            .orElseThrow(() -> new IllegalStateException("native host inspection is unavailable"));
    var open =
        MethodHandleProxies.asInterfaceInstance(
            OpenCall.class,
            Linker.nativeLinker()
                .downcallHandle(
                    address,
                    FunctionDescriptor.of(
                        ValueLayout.JAVA_INT,
                        ValueLayout.ADDRESS,
                        ValueLayout.JAVA_INT,
                        ValueLayout.JAVA_INT),
                    Linker.Option.firstVariadicArg(2)));
    return new LinuxHostDirectoryCalls(
        LinuxDirectoryCalls.create(os, architecture, symbols),
        LinuxInodeSecurity.create(os, architecture, symbols),
        open);
  }

  LinuxHostDirectoryCalls(DirectoryCalls children, InodeSecurityCalls security, OpenCall open) {
    this.children = Objects.requireNonNull(children, "children");
    this.security = Objects.requireNonNull(security, "security");
    this.open = Objects.requireNonNull(open, "open");
  }

  @Override
  public int openRoot() throws StorageIoException {
    if (security.effectiveUid() != 0) throw unavailable();
    try (Arena arena = Arena.ofConfined()) {
      // Sole fixed kernel magic-link exception. No user path, arbitrary PID, fallback or setns.
      int fd = open.call(arena.allocateFrom("/proc/1/root"), 0x10000 | 0x80000, 0);
      if (fd < 0) throw unavailable();
      return fd;
    }
  }

  @Override
  public int openDirectory(int parent, String name) throws StorageIoException {
    return children.openDirectory(parent, name);
  }

  @Override
  public int openEntry(int parent, String name) throws StorageIoException {
    return children.openEntry(parent, name);
  }

  @Override
  public void close(int descriptor) throws StorageIoException {
    children.close(descriptor);
  }

  @Override
  public int createFile(int parent, String name) throws StorageIoException {
    throw unavailable();
  }

  @Override
  public void createDirectory(int parent, String name) throws StorageIoException {
    throw unavailable();
  }

  @Override
  public void publish(int directory, String part, String ready) throws StorageIoException {
    throw unavailable();
  }

  @Override
  public void unlink(int directory, String name) throws StorageIoException {
    throw unavailable();
  }

  @Override
  public void sync(int directory) throws StorageIoException {
    throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
