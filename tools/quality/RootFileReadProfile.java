package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

/** BUG1332 primitive costs only: no original graph, DB, permit or actor authority. */
public final class RootFileReadProfile {
  private RootFileReadProfile() {}
  private static final Map<String, long[]> TIMES = new LinkedHashMap<>();

  private static void record(String phase, long began) {
    var v = TIMES.computeIfAbsent(phase, ignored -> new long[2]);
    v[0]++;
    v[1] += System.nanoTime() - began;
  }

  public static void main(String[] args) throws IOException {
    if (args.length != 0) throw new IllegalArgumentException("fixed primitive diagnostic");
    var io = new MaintenanceRunFiles.NioIo();
    var security = LinuxInodeSecurity.create();
    var root = OwnedTransferDirectory.open(LinuxHostDirectoryCalls.create(),
        Path.of("/var/lib/schubert-nk/maintenance"));
    ResourceScope.use(root::close, () -> root.atDirectory(held -> {
      for (int i = 0; i < 100; i++) {
        long at = System.nanoTime();
        if (io.attributes(held).isEmpty()) throw new IOException("metadata absent");
        record("attributes", at);
        at = System.nanoTime();
        if (io.filesystem(held).isEmpty()) throw new IOException("filesystem absent");
        record("filesystem", at);
        at = System.nanoTime();
        if (security.accessAcl(held, 44).length != 0) throw new IOException("unexpected ACL");
        record("acl", at);
        at = System.nanoTime();
        if (security.readOnlyFilesystem(held)) throw new IOException("unexpected readonly");
        record("readonly", at);
        at = System.nanoTime();
        if (!Files.getFileStore(Path.of("/proc")).type().equals("proc"))
          throw new IOException("unexpected proc filesystem");
        record("proc-filesystem", at);
        at = System.nanoTime();
        LinuxDirectoryCalls.create();
        record("directory-factory", at);
        at = System.nanoTime();
        LinuxInodeSecurity.create();
        record("security-factory", at);
      }
      return Boolean.TRUE;
    }));
    for (var e : TIMES.entrySet()) System.out.println("READONLY_PROFILE1 phase=" + e.getKey()
        + " count=" + e.getValue()[0] + " nanos=" + e.getValue()[1]);
  }
}
