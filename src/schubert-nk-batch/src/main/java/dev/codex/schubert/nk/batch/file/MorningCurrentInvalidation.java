package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;

/**
 * Same-run current INVALID transition after the parent's fresh eight-terminal observation while M,
 * A, DB/advisory and durable original remain held. No permit is issued and no backup/cleanup result
 * is inferred. NK-OPS-001; OPS009/UI251/SS341§5/343§6.15/SSC089/105; PG344/PT-OPS-MINVALID001
 * onward.
 */
@NullMarked
final class MorningCurrentInvalidation {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  interface Store {
    Epoch invalidate(UUID boot, UUID epoch, MaintenanceActivation activation) throws IOException;

    Epoch current() throws IOException;
  }

  private MorningCurrentInvalidation() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 6.15 fixes the root-owned tmpfs current namespace")
  static Epoch invalidate(
      RootStartupContext context, RootStartupContext.Snapshot expected, MaintenanceRunState state)
      throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root identity");
    Objects.requireNonNull(state, "same-run original");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    return ResourceScope.use(
        directory::close,
        () -> {
          var files = new StartupPermitFiles(directory, LinuxInodeSecurity.create());
          return invalidate(
              () -> context.recheck(expected),
              new Store() {
                @Override
                public Epoch invalidate(UUID boot, UUID epoch, MaintenanceActivation activation)
                    throws IOException {
                  return files.invalidate(boot, epoch, activation);
                }

                @Override
                public Epoch current() throws IOException {
                  return files.current();
                }
              },
              UUID.fromString(expected.boot()),
              UUID::randomUUID,
              state);
        });
  }

  static Epoch invalidate(
      Gate root, Store store, UUID boot, Supplier<UUID> epochs, MaintenanceRunState state)
      throws IOException {
    Objects.requireNonNull(root, "Morning root gate");
    Objects.requireNonNull(store, "current namespace");
    Objects.requireNonNull(boot, "kernel boot");
    Objects.requireNonNull(epochs, "new epoch source");
    Objects.requireNonNull(state, "same-run original");
    if (state.completion().isPresent()) throw unavailable();
    root.verify();
    UUID epoch = Objects.requireNonNull(epochs.get(), "new epoch");
    if (epoch.equals(boot)
        || epoch.equals(state.activation().id())
        || epoch.equals(state.activation().run().id())) throw unavailable();
    Epoch value =
        Objects.requireNonNull(
            store.invalidate(boot, epoch, state.activation()), "durable INVALID result");
    if (value.state() != StartupPermitRecords.State.INVALID
        || !value.boot().equals(boot)
        || !value.epoch().equals(epoch)
        || !value.activation().equals(state.activation())
        || value.permitDigest().isPresent()) throw unavailable();
    if (!value.equals(store.current())) throw unavailable();
    root.verify();
    return value;
  }

  private static IOException unavailable() {
    return new IOException("Morning current invalidation unavailable");
  }
}
