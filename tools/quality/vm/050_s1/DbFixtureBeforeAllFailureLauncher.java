import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.Collections;
import java.util.IdentityHashMap;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

/** Expected initialization failure only; no successful PT/coverage or runtime authority. */
public final class DbFixtureBeforeAllFailureLauncher {
  private DbFixtureBeforeAllFailureLauncher() {}

  public static void main(String[] arguments) {
    if (arguments == null || arguments.length != 0)
      throw new IllegalArgumentException("fixed lifecycle selector only");
    String root = System.getenv("SCHUBERT_PG_ROOT");
    if (!"/nonexistent-pgpt-dblife-noexec".equals(root)
        || !Files.notExists(Path.of(root, "lib/postgresql/18/bin/initdb")))
      throw new IllegalStateException("fixed nonexistent fixture executable required");
    var listener = new SummaryGeneratingListener();
    var launcher = LauncherFactory.create();
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(
        LauncherDiscoveryRequestBuilder.request()
            .selectors(
                DiscoverySelectors.selectMethod(
                    "dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest",
                    "exp3366001PriorSuccessRevalidatesEveryReadbackWithoutMutation"))
            .configurationParameter("junit.jupiter.execution.parallel.enabled", "false")
            .build());
    var result = listener.getSummary();
    boolean initializationIo = false;
    boolean nullPointer = false;
    var pending = new ArrayDeque<Throwable>();
    var seen = Collections.newSetFromMap(new IdentityHashMap<Throwable, Boolean>());
    for (var failure : result.getFailures()) pending.add(failure.getException());
    while (!pending.isEmpty()) {
      var current = pending.removeFirst();
      if (!seen.add(current)) continue;
      if (seen.size() > 128) throw new IllegalStateException("bounded failure chain required");
      nullPointer |= current instanceof NullPointerException;
      for (var frame : current.getStackTrace())
        if (current instanceof IOException
            && frame
                .getClassName()
                .equals("dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest")
            && frame.getMethodName().equals("start")) initializationIo = true;
      if (current.getCause() != null) pending.add(current.getCause());
      Collections.addAll(pending, current.getSuppressed());
    }
    if (result.getTestsFoundCount() != 1
        || result.getTestsStartedCount() != 0
        || result.getTestsSucceededCount() != 0
        || result.getTestsFailedCount() != 0
        || result.getTestsSkippedCount() != 0
        || result.getTestsAbortedCount() != 0
        || result.getContainersFailedCount() != 1
        || result.getContainersAbortedCount() != 0
        || !initializationIo
        || nullPointer)
      throw new IllegalStateException("original initialization IO without secondary NPE required");
    System.out.println(
        "DBLIFE_FOUND=1 STARTED=0 CONTAINER_FAILED=1 BEFOREALL_IO=true SECONDARY_NPE=false PT_CREDIT=0");
  }
}
