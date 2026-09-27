import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.*;

/** PT-OPS-NATIVE-013: A root adapter under real private namespace; not whole authorization. */
public final class NativeStartupAdmissionProbe {
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root fixture required");
    var observed = StartupAdmissionFile.create().tryExclusive(fd -> {
      if (fd < 128 || fd > 65535) throw new AssertionError("reserved A required");
      try (var descriptors = Files.list(Path.of("/proc/self/fd"))) {
        for (Path descriptor : descriptors.toList()) {
          if (!Files.exists(descriptor)) continue; // directory enumeration may include closed stream FD
          Path target = Files.readSymbolicLink(descriptor);
          if (target.equals(Path.of("/")) || target.equals(Path.of("/run"))
              || target.equals(Path.of("/run/schubert-nk")))
            throw new AssertionError("observation root FD remains live");
        }
      }
      return Boolean.TRUE;
    });
    if (!observed.equals(java.util.Optional.of(Boolean.TRUE))) throw new AssertionError("isolated A contended");
    System.out.println("PT-OPS-NATIVE-013 PASS hostPrivateIdentity=true crossNamespaceFlock=true observationRootFdClosedBeforeCallback=true borrowedReservedA=true fullGate=false");
  }
}
