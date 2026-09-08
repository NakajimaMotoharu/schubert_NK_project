package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.extension.AnnotatedElementContext;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.io.TempDirFactory;

/**
 * PT-SCN-009-T07: test-only access to internal real providers, never broadens production
 * visibility.
 */
public final class RealScenarioFileFixture implements AutoCloseable {
  public static final class Ext4 implements TempDirFactory {
    @Override
    public Path createTempDirectory(AnnotatedElementContext element, ExtensionContext context)
        throws IOException {
      return Files.createTempDirectory(Path.of("target").toAbsolutePath(), "scenario-stage-real-");
    }
  }

  private final OwnedTransferDirectory held;
  private final ScenarioFilePublisher publisher;
  private final ScenarioFileInspector inspector;

  public RealScenarioFileFixture(Path root) throws IOException {
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
    Files.setAttribute(
        root,
        "posix:group",
        root.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByGroupName("users"));
    var attributes = Files.readAttributes(root, PosixFileAttributes.class);
    var identity = new StorageIdentity(attributes.owner().getName(), "users");
    held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
    var ids = new AtomicInteger();
    publisher =
        new ScenarioFileWriter(
            held,
            identity,
            new TransferCapacity(0, 0),
            () -> new UUID(0, 1000 + ids.incrementAndGet()));
    inspector = new ScenarioReadyFileInspector(held, identity);
  }

  public ScenarioFilePublisher publisher() {
    return publisher;
  }

  public ScenarioFileInspector inspector() {
    return inspector;
  }

  @Override
  public void close() throws IOException {
    held.close();
  }
}
