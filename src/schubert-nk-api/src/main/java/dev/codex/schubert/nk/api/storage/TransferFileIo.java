package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import java.io.IOException;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;

/**
 * Scoped held-inode I/O only; no path escapes. NK-SCN-001; RD FIL-001..009; UI237/243;
 * SS333/342/343; SSC-020/PG-D-060; PT-SCN-008-W07..W09.
 */
interface TransferFileIo {
  void initializeDirectory(Path handle) throws IOException;

  LargeResultContent writePart(Path handle, ScenarioRecordStream records)
      throws IOException, NoSuchAlgorithmException;

  void verify(Path handle, LargeResultContent content) throws IOException, NoSuchAlgorithmException;
}
