package dev.codex.schubert.nk.batch.platform;

/** PT-ROOTGUARD-001..003: existing package-private port, forbidden I/O never returns success. */
public final class RootContextNoIoFixture {
  private int calls;
  private final RootStartupContext context =
      new RootStartupContext(
          new RootStartupContext.Io() {
            @Override
            public long effectiveUid() {
              throw denied();
            }

            @Override
            public long pid() {
              throw denied();
            }

            @Override
            public String procFilesystem() {
              throw denied();
            }

            @Override
            public String initExecutable() {
              throw denied();
            }

            @Override
            public byte[] boot() {
              throw denied();
            }

            @Override
            public byte[] stat(long pid) {
              throw denied();
            }

            @Override
            public byte[] cgroup(long pid) {
              throw denied();
            }

            @Override
            public byte[] unit(RootStartupContext.Service service) {
              throw denied();
            }

            @Override
            public long serviceRootUid(long pid) {
              throw denied();
            }

            @Override
            public byte[] unitDeadline(RootStartupContext.Service service) {
              throw denied();
            }

            @Override
            public String invocation() {
              throw denied();
            }
          });

  private AssertionError denied() {
    calls++;
    return new AssertionError("forbidden native fixture I/O");
  }

  public RootStartupContext context() {
    return context;
  }

  public int calls() {
    return calls;
  }
}
