package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.time.Instant;
import java.util.Objects;

/**
 * Internal Transfer-only preparation within a caller-owned exclusive startup interval. Probe must
 * finish before the complete scan seeds quota. This does not prove single-instance ownership, the
 * other roots, credentials or API readiness; its result must not be registered before those gates.
 * NK-SCN-001; RD FIL-001..009; UI237/243; SS311/333 §7.4/§13/342; PG259/PT-SCN-008-P04/P05.
 */
final class TransferStoragePreparation {
  private TransferStoragePreparation() {}

  static Prepared prepare(OwnedTransferDirectory root, StorageIdentity identity, Instant now)
      throws StorageIoException {
    Objects.requireNonNull(root, "root");
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(now, "now");
    new TransferStartupProbe(root, identity).verify(now);
    var usage = new TransferUsageScanner().scan(root, identity);
    var capacity = new TransferCapacity(usage.bytes(), usage.files());
    return new Prepared(
        new ScenarioFileWriter(root, identity, capacity),
        new ScenarioReadyFileInspector(root, identity),
        capacity);
  }

  record Prepared(
      ScenarioFilePublisher publisher, ScenarioFileInspector inspector, TransferCapacity capacity) {
    Prepared {
      Objects.requireNonNull(publisher, "publisher");
      Objects.requireNonNull(inspector, "inspector");
      Objects.requireNonNull(capacity, "capacity");
    }

    TransferCapacity.Snapshot usage() {
      return capacity.snapshot();
    }
  }
}
