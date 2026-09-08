package dev.codex.schubert.nk.api.storage;

import java.io.IOException;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;

/**
 * Internal scoped diagnostic I/O, no property-controlled failpoints. NK-SCN-001; UI237/243; SS333
 * §7.4; SSC-022; PT-SCN-008-P01..P03.
 */
interface ProbeFileIo {
  void initializeDirectory(Path handle) throws IOException;

  void write(Path handle, boolean second) throws IOException, NoSuchAlgorithmException;

  void verify(Path handle, boolean second) throws IOException, NoSuchAlgorithmException;
}
