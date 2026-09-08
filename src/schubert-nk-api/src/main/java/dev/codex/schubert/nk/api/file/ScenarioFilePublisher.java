package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import java.io.IOException;
import java.time.Instant;
import java.util.List;

/**
 * Publish already validated immutable records after DB commit; return a verified ready descriptor.
 * NK-SCN-001; UI234/237; SS311/333 §4..6; PT-SCN-008-R02/R03/F04. No delete-on-response-failure
 * API.
 */
@FunctionalInterface
public interface ScenarioFilePublisher {
  LargeResultDescriptor publish(List<ScenarioEntryRecord> records, Instant generatedAt)
      throws IOException;
}
