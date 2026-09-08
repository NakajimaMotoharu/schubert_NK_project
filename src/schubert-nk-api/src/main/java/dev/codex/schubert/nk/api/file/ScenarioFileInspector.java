package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import java.io.IOException;

/**
 * Read-only physical replay check, outside DB TX; only confirmed absence permits regeneration.
 * NK-SCN-001; FIL-001..009/MQ-006..010; UI237/241; SS324 §7.1/333 §6; SSC-027/PT-SCN-009-V01..V03.
 * Invalid/unreadable files throw, never return MISSING.
 */
@FunctionalInterface
public interface ScenarioFileInspector {
  enum Availability {
    PRESENT,
    MISSING
  }

  Availability inspect(LargeResultDescriptor descriptor) throws IOException;
}
