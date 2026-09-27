import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;
import java.nio.file.*;

/** PT-OPS-NATIVE-009: fixed VM-only host/private mount feasibility, NOT Production admission. */
public final class NativeHostViewProbe {
  @SuppressWarnings("restricted")
  public static void main(String[] args) throws Throwable {
    if (args.length != 0 || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root fixture required");
    var linker = Linker.nativeLinker();
    MethodHandle open = linker.downcallHandle(linker.defaultLookup().find("openat").orElseThrow(),
        FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.ADDRESS,
            ValueLayout.JAVA_INT, ValueLayout.JAVA_INT), Linker.Option.firstVariadicArg(3));
    var calls = LinuxDirectoryCalls.create();
    try (var arena = Arena.ofConfined()) {
      // Deliberate fixed kernel magic link. Production policy/provenance is not implemented here.
      int root = (int) open.invokeExact(-100, arena.allocateFrom("/proc/1/root"), 0x10000 | 0x80000, 0);
      if (root < 0) throw new AssertionError("host root access failed");
      try {
        int run = calls.openDirectory(root, "run");
        try {
          var held = Path.of("/proc/self/fd/" + run);
          var security = LinuxInodeSecurity.create();
          boolean privateReadOnly;
          try (var serviceRun = OwnedTransferDirectory.open(calls, Path.of("/run"))) {
            privateReadOnly = serviceRun.atDirectory(security::readOnlyFilesystem);
          }
          boolean hostReadOnly = security.readOnlyFilesystem(held);
          var actual = Files.readAttributes(held, "unix:dev,ino,uid,gid,mode");
          var service = Files.readAttributes(Path.of("/run"), "unix:dev,ino,uid,gid,mode");
          System.out.println("PT-OPS-NATIVE-009 OBSERVE privateReadOnly=" + privateReadOnly
              + " hostReadOnly=" + hostReadOnly + " sameDevInodeOwnerMode=" + actual.equals(service)
              + " javaFileStoreHostReadOnly=" + Files.getFileStore(held).isReadOnly());
          if (!privateReadOnly || hostReadOnly || !actual.equals(service))
            throw new AssertionError("private/host mount observation mismatch");
          System.out.println("PT-OPS-NATIVE-009 PASS privateReadOnly=true hostReadOnly=false sameDevInodeOwnerMode=true productionAdmission=false");
        } finally { calls.close(run); }
      } finally { calls.close(root); }
    }
  }
}
