package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Actual two-level retained Transfer cleanup. Never opens caller paths or recursively deletes.
 * Parent authenticates fixed root, M/A, dedicated DB advisory, stopped applications and total
 * budget through every guard. NK-BAT-001/FIL006/OPS009/UI237/251/SS333§12/341; SSC117/118;
 * PT-OPS-TRANSFER001..003. This file result alone is not a durable DB terminal or startup permit.
 * PG-D503/1483: read-only IO fault contracts and PT-OPS-TRANSFER-IO-001..008; admission unchanged.
 */
@NullMarked
final class TransferCleanup {
  @FunctionalInterface
  interface Guard {
    void verify() throws IOException;
  }

  /** Borrowed read-only port; held paths and all mutation remain with the existing FD owner. */
  interface Io {
    @Nullable Map<String, Object> metadata(Path held) throws IOException;

    @Nullable String filesystem(Path held) throws IOException;

    @Nullable DirectoryStream<Path> openNames(Path held) throws IOException;
  }

  static final class NioIo implements Io {
    @Override
    public Map<String, Object> metadata(Path held) throws IOException {
      return Files.readAttributes(held, "unix:*");
    }

    @Override
    public String filesystem(Path held) throws IOException {
      return Files.getFileStore(held).type();
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      return Files.newDirectoryStream(held);
    }
  }

  record Outcome(long target, long success, long failure, long retained, long bytes) {
    Outcome {
      if (target < 0
          || success < 0
          || failure < 0
          || retained < 0
          || bytes < 0
          || success > target
          || failure != target - success)
        throw new IllegalArgumentException("transfer counters invalid");
    }

    BatchStepResult result() {
      return new BatchStepResult(
          failure != 0 || retained != 0
              ? BatchStepResult.Status.WARNING
              : BatchStepResult.Status.SUCCESS,
          target,
          success,
          failure,
          bytes,
          failure != 0
              ? BatchStepResult.Reason.IO_FAILURE
              : retained != 0
                  ? BatchStepResult.Reason.PROTECTED_RECORDS
                  : BatchStepResult.Reason.NONE);
    }

    @Override
    public String toString() {
      return "TransferCleanupOutcome[counts=<redacted>]";
    }
  }

  private static final int MINIMUM_SUPPORTED_DATE_YEAR = 1;
  private static final DateTimeFormatter DATE =
      DateTimeFormatter.ofPattern("uuuuMMdd").withResolverStyle(ResolverStyle.STRICT);
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final long uid;
  private final long gid;
  private final Guard guard;
  private final Io io;

  TransferCleanup(
      OwnedTransferDirectory root, InodeSecurityCalls security, long uid, long gid, Guard guard) {
    this(root, security, uid, gid, guard, new NioIo());
  }

  TransferCleanup(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      long uid,
      long gid,
      Guard guard,
      Io io) {
    this.root = Objects.requireNonNull(root, "retained fixed Transfer root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.guard = Objects.requireNonNull(guard, "same owner/budget/advisory/application gate");
    this.io = Objects.requireNonNull(io, "transfer read IO");
    if (uid < 1 || uid > 4294967294L || gid < 1 || gid > 4294967294L)
      throw new IllegalArgumentException("transfer identity invalid");
    this.uid = uid;
    this.gid = gid;
  }

  Outcome execute(Instant cutoff) throws IOException {
    Objects.requireNonNull(cutoff, "original cutoff");
    guard.verify();
    Metadata admitted = root.atDirectory(path -> inspect(path, true, -1));
    var counts = new Counts();
    for (String name : names(root)) {
      checkRoot(admitted);
      LocalDate date;
      try {
        if (!name.matches("[0-9]{8}")) {
          counts.retained();
          continue;
        }
        date = LocalDate.parse(name, DATE);
        // Eight ASCII digits and adjacent strict uuuu/MM/dd already bound the year to 0..9999.
        if (date.getYear() < MINIMUM_SUPPORTED_DATE_YEAR) {
          counts.retained();
          continue;
        }
      } catch (DateTimeException invalidName) {
        counts.retained();
        continue;
      }
      Metadata before;
      try {
        before = root.atExistingEntryHandle(name, path -> inspect(path, true, admitted.device()));
      } catch (IOException unsafeEntry) {
        counts.retained();
        continue;
      }
      guard.verify();
      ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
          () -> root.openExistingDate(date),
          OwnedTransferDirectory::close,
          child -> {
            require(
                sameDirectory(
                    before, child.atDirectory(path -> inspect(path, true, admitted.device()))));
            for (String file : names(child)) {
              checkRoot(admitted);
              if (!file.matches(
                  "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.(part|ready)")) {
                counts.retained();
                continue;
              }
              Metadata value;
              try {
                value =
                    child.atExistingEntryHandle(
                        file, path -> inspect(path, false, admitted.device()));
              } catch (IOException unsafeEntry) {
                counts.retained();
                continue;
              }
              if (!value.modified().toInstant().isBefore(cutoff)) {
                counts.retained();
                continue;
              }
              // Guard failures propagate, rather than being normalized into a recoverable file
              // warning.
              checkRoot(admitted);
              require(
                  sameDirectory(
                      before, child.atDirectory(path -> inspect(path, true, admitted.device()))));
              try {
                require(
                    value.equals(
                        child.atExistingEntryHandle(
                            file, path -> inspect(path, false, admitted.device()))));
                child.unlinkEntry(file);
                require(child.atDirectory(path -> absent(path.resolve(file))));
                counts.deleted(value.size());
              } catch (IOException actualFileFailure) {
                counts.failed();
              }
              checkRoot(admitted);
            }
            checkRoot(admitted);
            require(
                sameDirectory(
                    before, child.atDirectory(path -> inspect(path, true, admitted.device()))));
            if (names(child).isEmpty()) {
              require(
                  sameDirectory(
                      before,
                      root.atExistingEntryHandle(
                          name, path -> inspect(path, true, admitted.device()))));
              root.removeEmptyChild(name);
              require(root.atDirectory(path -> absent(path.resolve(name))));
            }
            checkRoot(admitted);
            return Boolean.TRUE;
          });
    }
    checkRoot(admitted);
    return counts.outcome();
  }

  private void checkRoot(Metadata admitted) throws IOException {
    guard.verify();
    require(
        sameDirectory(admitted, root.atDirectory(path -> inspect(path, true, admitted.device()))));
    guard.verify();
  }

  private Metadata inspect(Path held, boolean directory, long device) throws IOException {
    Metadata m = EnvironmentInodePolicy.metadata(io.metadata(held));
    require(
        m.mode() == (directory ? 0x41e8 : 0x81a0)
            && m.uid() == uid
            && m.gid() == gid
            && m.size() >= 0
            && (directory ? m.links() >= 2 : m.links() == 1)
            && (device == -1 || m.device() == device));
    byte[] acl = security.accessAcl(held, 44);
    require(acl != null && acl.length == 0 && !security.readOnlyFilesystem(held));
    String filesystem = io.filesystem(held);
    require(
        filesystem != null
            && List.of("ext2", "ext3", "ext4", "xfs", "btrfs", "tmpfs").contains(filesystem));
    return m;
  }

  private static boolean sameDirectory(Metadata first, Metadata next) {
    // Each operand is directory-admitted by inspect with the fixed UID/GID/mode/device.
    // Keep fresh admission at ALL five callers; only inode is not fixed by that admission.
    return first.inode() == next.inode();
  }

  private static boolean absent(Path path) throws IOException {
    try {
      Files.readAttributes(path, "unix:*", java.nio.file.LinkOption.NOFOLLOW_LINKS);
      return false;
    } catch (java.nio.file.NoSuchFileException confirmedMissing) {
      return true;
    }
  }

  private List<String> names(OwnedTransferDirectory directory) throws IOException {
    return directory.atDirectory(
        path -> {
          var result = new ArrayList<String>();
          var opened = io.openNames(path);
          if (opened == null) throw new IOException("transfer enumeration unavailable");
          try (var entries = opened) {
            for (Path entry : entries) {
              Path name = entry == null ? null : entry.getFileName();
              if (name == null) throw new IOException("transfer entry invalid");
              result.add(name.toString());
            }
          } catch (DirectoryIteratorException failure) {
            throw new IOException("transfer enumeration unavailable");
          }
          result.sort(String::compareTo);
          return List.copyOf(result);
        });
  }

  private static final class Counts {
    private long target;
    private long success;
    private long failure;
    private long retainedRetained;
    private long bytes;

    void retained() {
      retainedRetained = Math.addExact(retainedRetained, 1);
    }

    void failed() {
      target = Math.addExact(target, 1);
      failure = Math.addExact(failure, 1);
    }

    void deleted(long size) {
      target = Math.addExact(target, 1);
      success = Math.addExact(success, 1);
      bytes = Math.addExact(bytes, size);
    }

    Outcome outcome() {
      return new Outcome(target, success, failure, retainedRetained, bytes);
    }
  }
}
