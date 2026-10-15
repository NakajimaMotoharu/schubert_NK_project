package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.DateTimeException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Objects;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Complete, bounded metadata scan before producers start; no live concurrent-writer snapshot claim.
 * NK-SCN-001; RD FIL/PER; UI237/243; SS333 §13; PG-D-063; PT-SCN-008-U01..U03.
 */
final class TransferUsageScanner {
  private static final Pattern DATE = Pattern.compile("[0-9]{8}");
  private static final Pattern ENTRY =
      Pattern.compile(
          "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.(part|ready)");
  private final DirectoryEntries entries;

  @FunctionalInterface
  interface DirectoryEntries {
    DirectoryStream<Path> open(Path heldDirectory) throws IOException;
  }

  /** Unix file size, not allocated disk blocks; incomplete scans never return this value. */
  record Usage(long bytes, long files) {
    Usage {
      if (files < 0 || files > 10000 || bytes < 0 || bytes > files * 48_000_000L) {
        throw new IllegalArgumentException("invalid bounded transfer usage");
      }
    }
  }

  TransferUsageScanner() {
    this(Files::newDirectoryStream);
  }

  TransferUsageScanner(DirectoryEntries entries) {
    this.entries = Objects.requireNonNull(entries, "entries");
  }

  Usage scan(OwnedTransferDirectory root, StorageIdentity identity) throws StorageIoException {
    Objects.requireNonNull(root, "root");
    Objects.requireNonNull(identity, "identity");
    TransferRootInspection.inspect(root, identity);
    try {
      return root.atDirectory(handle -> scanDates(root, identity, handle));
    } catch (StorageIoException
        | DirectoryIteratorException
        | DateTimeException
        | IllegalArgumentException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  private Usage scanDates(OwnedTransferDirectory root, StorageIdentity identity, Path handle)
      throws IOException {
    long bytes = 0;
    long files = 0;
    try (var dates = entries.open(handle)) {
      for (Path candidate : dates) {
        String name = Objects.requireNonNull(candidate.getFileName(), "date name").toString();
        if (!DATE.matcher(name).matches())
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        LocalDate date = LocalDate.parse(name, DateTimeFormatter.BASIC_ISO_DATE);
        try (var day = root.openExistingDate(date)) {
          long remaining = 10000 - files;
          Usage usage = day.atDirectory(path -> scanFiles(day, identity, path, remaining));
          bytes += usage.bytes();
          files += usage.files();
        }
      }
    }
    return new Usage(bytes, files);
  }

  private Usage scanFiles(
      OwnedTransferDirectory day, StorageIdentity identity, Path handle, long remaining)
      throws IOException {
    StorageAttributeGuard.directory(
        Files.readAttributes(handle, "unix:owner,group,mode,nlink"), identity);
    long bytes = 0;
    long files = 0;
    try (var candidates = entries.open(handle)) {
      for (Path candidate : candidates) {
        String name = Objects.requireNonNull(candidate.getFileName(), "entry name").toString();
        if (!ENTRY.matcher(name).matches() || files >= remaining)
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        UUID id = UUID.fromString(name.substring(0, 36));
        boolean ready = name.endsWith(".ready");
        OwnedTransferDirectory.FileOperation<Long> inspect =
            path ->
                StorageAttributeGuard.transferSize(
                    Files.readAttributes(path, "unix:owner,group,mode,nlink,size"),
                    identity,
                    ready);
        bytes += ready ? day.atReadyHandle(id, inspect) : day.atPartHandle(id, inspect);
        files++;
      }
    }
    return new Usage(bytes, files);
  }
}
