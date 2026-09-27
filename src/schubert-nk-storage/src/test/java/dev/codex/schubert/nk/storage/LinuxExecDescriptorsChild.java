package dev.codex.schubert.nk.storage;

import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** Test-only owned FD reservation/native flock oracle; not root/sealed-proof admission. */
public final class LinuxExecDescriptorsChild {
  private LinuxExecDescriptorsChild() {}

  @SuppressWarnings("restricted")
  public static void main(String[] args) throws Throwable {
    var symbols = Linker.nativeLinker().defaultLookup();
    var linker = Linker.nativeLinker();
    MethodHandle open =
        linker.downcallHandle(
            symbols.find("open").orElseThrow(),
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.firstVariadicArg(2));
    MethodHandle fcntl =
        linker.downcallHandle(
            symbols.find("fcntl").orElseThrow(),
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.firstVariadicArg(2));
    MethodHandle flock =
        linker.downcallHandle(
            symbols.find("flock").orElseThrow(),
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT));
    MethodHandle close =
        linker.downcallHandle(
            symbols.find("close").orElseThrow(),
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT));
    try (var directory =
            OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of(args[0]));
        var executable =
            OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/usr/bin"))) {
      directory.atExistingEntryHandle(
          "lock",
          file -> {
            // The retained capability is O_PATH; flock needs a separate read-only open of it.
            int original = nativeOpen(open, file);
            try {
              int first = nativeDuplicate(fcntl, original, 128);
              try {
                int second = nativeDuplicate(fcntl, first, 129);
                try {
                  nativeLock(flock, first);
                  executable.atExistingEntryHandle(
                      "python3.14",
                      held -> {
                        LinuxExecDescriptors.create()
                            .withInherited(
                                first,
                                second,
                                () ->
                                    LinuxProcessExec.create()
                                        .replace(
                                            held,
                                            List.of(
                                                "python3.14",
                                                "-u",
                                                "-c",
                                                "import os,fcntl,sys; assert fcntl.fcntl(128,fcntl.F_GETFD)==0; assert fcntl.fcntl(129,fcntl.F_GETFD)==0; print('PID='+str(os.getpid())+' INHERITED=128,129'); assert sys.stdin.readline()=='\\n'"),
                                            Map.of()));
                        throw new AssertionError("replacement cannot return");
                      });
                } finally {
                  nativeClose(close, second);
                }
              } finally {
                nativeClose(close, first);
              }
              throw new AssertionError("replacement cannot return");
            } finally {
              nativeClose(close, original);
            }
          });
    }
  }

  private static int nativeDuplicate(MethodHandle fcntl, int fd, int minimum) {
    try {
      int result = (int) fcntl.invokeExact(fd, 1030, minimum); // F_DUPFD_CLOEXEC
      if (result != minimum) throw new AssertionError("fixture descriptor reservation failed");
      return result;
    } catch (Throwable failure) {
      throw new AssertionError("fixture native duplicate failed", failure);
    }
  }

  private static int nativeOpen(MethodHandle open, Path held) {
    try (var arena = Arena.ofConfined()) {
      int result = (int) open.invokeExact(arena.allocateFrom(held.toString()), 0x80000, 0);
      if (result < 0) throw new AssertionError("fixture read-only open failed");
      return result;
    } catch (Throwable failure) {
      throw new AssertionError("fixture native open failed", failure);
    }
  }

  private static void nativeLock(MethodHandle flock, int fd) {
    try {
      if ((int) flock.invokeExact(fd, 6) != 0) throw new AssertionError("fixture lock failed");
    } catch (Throwable failure) {
      throw new AssertionError("fixture native flock failed", failure);
    }
  }

  private static void nativeClose(MethodHandle close, int fd) {
    try {
      if ((int) close.invokeExact(fd) != 0) throw new AssertionError("fixture close failed");
    } catch (Throwable failure) {
      throw new AssertionError("fixture native close failed", failure);
    }
  }
}
