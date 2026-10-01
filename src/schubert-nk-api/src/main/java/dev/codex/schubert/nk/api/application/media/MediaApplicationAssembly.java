package dev.codex.schubert.nk.api.application.media;

import dev.codex.schubert.nk.api.file.MediaFileInspector;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Existing staged Media graph, borrowed codecs/held inspector/database. No root admission, DB
 * transaction, consumer or ready publication here. NK-MED-001; FIL006007/AUT001/MQ006..010;
 * UI226232237243; SS312324333342343/SSC150; PT-MED-ASSEMBLY-001..003.
 */
public final class MediaApplicationAssembly {
  private MediaApplicationAssembly() {}

  public static MediaApplicationService create(
      DataSource database,
      FingerprintKeyRing fingerprints,
      ResponseSnapshotCodec snapshots,
      MediaFileInspector inspector,
      Clock clock)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(database, "database");
    Objects.requireNonNull(fingerprints, "fingerprints");
    Objects.requireNonNull(snapshots, "snapshots");
    Objects.requireNonNull(inspector, "inspector");
    Objects.requireNonNull(clock, "clock");
    return new MediaApplicationService(
        database,
        new AuthenticationContextVerifier(new ContextHash()),
        new MediaRepository(),
        new JdbcInboxCoordinator(fingerprints),
        new MediaReplayService(snapshots),
        inspector,
        clock);
  }
}
