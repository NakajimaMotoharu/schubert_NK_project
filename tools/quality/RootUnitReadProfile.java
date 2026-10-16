package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

/** BUG1332 read-only timing; never a Root/permit/actor or coverage qualification. */
public final class RootUnitReadProfile {
  private RootUnitReadProfile() {}

  private static final Map<String, long[]> TIMES = new LinkedHashMap<>();

  private static void record(String phase, long began) {
    long[] value = TIMES.computeIfAbsent(phase, ignored -> new long[2]);
    value[0]++;
    value[1] += System.nanoTime() - began;
  }

  public static void main(String[] args) throws IOException {
    if (args.length != 0) throw new IllegalArgumentException("fixed read-only profile");
    var factory = new LinuxSystemdSession.Factory();
    LinuxSystemdQuery.Factory measured =
        () -> {
          long began = System.nanoTime();
          var actual = factory.create();
          record("factory", began);
          return new LinuxSystemdQuery.Session() {
            public void start(LinuxSystemdQuery.Budget budget) throws IOException {
              long at = System.nanoTime();
              try { actual.start(budget); } finally { record("start", at); }
            }

            public LinuxSystemdQuery.Owner owner(long remaining) throws IOException {
              long at = System.nanoTime();
              try { return actual.owner(remaining); } finally { record("owner", at); }
            }

            public String read(RootStartupContext.Service service, LinuxSystemdQuery.Property property, long remaining) throws IOException {
              long at = System.nanoTime();
              try { return actual.read(service, property, remaining); } finally { record("property-" + property.name(), at); }
            }

            public void close() throws IOException {
              long at = System.nanoTime();
              try { actual.close(); } finally { record("close", at); }
            }

            public boolean closed() { return actual.closed(); }
          };
        };
    var query = new LinuxSystemdQuery(measured, System::nanoTime);
    long began = System.nanoTime();
    for (int i = 0; i < 5; i++) {
      byte[] raw = query.read(RootStartupContext.Service.API,
          "Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup");
      if (raw.length == 0 || raw.length > 4096) throw new IOException("profile projection");
      Arrays.fill(raw, (byte) 0);
    }
    record("total", began);
    for (var entry : TIMES.entrySet()) {
      System.out.println("READONLY_PROFILE1 phase=" + entry.getKey()
          + " count=" + entry.getValue()[0] + " nanos=" + entry.getValue()[1]);
    }
  }
}
