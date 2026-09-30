package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Closed public data correlation, never authorization. NK-OPS-001/UI251/SS343 SSC124/CFREQ001. */
@NullMarked
public sealed interface CleanupProfile permits CleanupWorkerRequest, CleanupFailedBackupRequest {
  int MAXIMUM_BYTES = 1024;

  byte[] encode();

  java.util.UUID run();

  java.util.UUID activation();

  java.time.Instant cutoff();

  static CleanupProfile consume(byte[] owned) {
    Objects.requireNonNull(owned, "owned profile");
    try {
      if (owned.length < 1 || owned.length > MAXIMUM_BYTES)
        throw new IllegalArgumentException("cleanup profile invalid");
      String header = new String(owned, 0, Math.min(owned.length, 13), StandardCharsets.US_ASCII);
      if (header.startsWith("NKCLEAN1\n")) return CleanupWorkerRequest.consume(owned);
      if (header.startsWith("NKCLEANFAIL1\n")) return CleanupFailedBackupRequest.consume(owned);
      throw new IllegalArgumentException("cleanup profile invalid");
    } finally {
      Arrays.fill(owned, (byte) 0);
    }
  }
}
