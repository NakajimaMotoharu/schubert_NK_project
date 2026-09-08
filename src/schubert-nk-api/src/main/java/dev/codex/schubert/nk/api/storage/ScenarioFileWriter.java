package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * API-internal publisher; caller admits/owns root and scan-initialized quota, commits snapshot
 * before invocation. Not registered with a service until full startup readiness is implemented.
 * NK-SCN-001; RD FIL/PER; UI234/237/243; SS333/342/343; SSC-019/020; PG-D-060; PT-SCN-008-W07..W10.
 * Ready files are never deleted by this class.
 */
final class ScenarioFileWriter implements ScenarioFilePublisher {
  private static final ZoneId JST = ZoneId.of("Asia/Tokyo");
  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;
  private final TransferCapacity capacity;
  private final Supplier<UUID> identifiers;
  private final TransferFileIo fileIo;

  ScenarioFileWriter(
      OwnedTransferDirectory root, StorageIdentity identity, TransferCapacity capacity) {
    this(root, identity, capacity, UUID::randomUUID);
  }

  ScenarioFileWriter(
      OwnedTransferDirectory root,
      StorageIdentity identity,
      TransferCapacity capacity,
      Supplier<UUID> identifiers) {
    this(root, identity, capacity, identifiers, new HeldTransferFileIo(identity));
  }

  ScenarioFileWriter(
      OwnedTransferDirectory root,
      StorageIdentity identity,
      TransferCapacity capacity,
      Supplier<UUID> identifiers,
      TransferFileIo fileIo) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
    this.capacity = Objects.requireNonNull(capacity, "capacity");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.fileIo = Objects.requireNonNull(fileIo, "fileIo");
  }

  @Override
  public LargeResultDescriptor publish(List<ScenarioEntryRecord> records, Instant generatedAt)
      throws StorageIoException {
    Objects.requireNonNull(generatedAt, "generatedAt");
    var prepared = new ScenarioRecordStream(records);
    LocalDate date = LocalDate.ofInstant(generatedAt, JST);
    if (date.getYear() < 1 || date.getYear() > 9999) {
      throw new IllegalArgumentException("invalid scenario publication date");
    }
    TransferRootInspection.inspect(root, identity);
    for (int attempt = 0; ; attempt++) {
      Optional<LargeResultDescriptor> result;
      try (var reservation = capacity.reserve(prepared.byteLength())) {
        UUID id = Objects.requireNonNull(identifiers.get(), "generated file ID");
        result = publishAttempt(prepared, date, id, reservation);
      }
      // Retry begins only after the attempt's directory and reservation have both closed.
      if (result.isPresent()) return result.orElseThrow();
      if (attempt >= 3) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private Optional<LargeResultDescriptor> publishAttempt(
      ScenarioRecordStream prepared,
      LocalDate date,
      UUID id,
      TransferCapacity.Reservation reservation)
      throws StorageIoException {
    Optional<LargeResultDescriptor> result;
    try (var directory =
        root.openDate(
            date,
            handle -> {
              fileIo.initializeDirectory(handle);
              return Boolean.TRUE;
            })) {
      directory.atDirectory(
          handle -> {
            StorageAttributeGuard.directory(
                Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
            return Boolean.TRUE;
          });
      var state = new Attempt();
      try {
        LargeResultContent content =
            directory.createPart(
                id,
                handle -> {
                  state.created = true;
                  return Objects.requireNonNull(
                      fileIo.writePart(handle, prepared), "written content");
                });
        directory.publish(id);
        state.published = true;
        reservation.retain();
        directory.atReadyHandle(
            id,
            handle -> {
              fileIo.verify(handle, content);
              return Boolean.TRUE;
            });
        result =
            Optional.of(
                new LargeResultDescriptor(
                    id,
                    date.format(DateTimeFormatter.BASIC_ISO_DATE) + "/" + id + ".ready",
                    content.byteLength(),
                    content.sha256(),
                    content.recordCount()));
      } catch (StorageIoException | RuntimeException failure) {
        if (state.created && !state.published) {
          try {
            directory.deletePart(id);
          } catch (StorageIoException cleanupFailure) {
            // MISSING also covers rename success followed by fsync failure: retain all.
            reservation.retain();
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
        if (!state.published
            && failure instanceof StorageIoException storage
            && storage.reason() == StorageIoException.Reason.COLLISION) {
          result = Optional.empty();
        } else {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        }
      }
    } catch (StorageIoException | RuntimeException failure) {
      // Includes directory close and compound failures; never expose physical paths.
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    return result;
  }

  /** Request-local only; never exposed to another thread or reused for a collision retry. */
  private static final class Attempt {
    boolean created;
    boolean published;
  }
}
