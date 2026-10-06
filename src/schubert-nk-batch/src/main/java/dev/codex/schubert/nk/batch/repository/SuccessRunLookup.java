package dev.codex.schubert.nk.batch.repository;

import java.io.IOException;
import java.time.Instant;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * SSC200 / RLOOK200002: callback to the same still-owned original Session, data not authority.
 * NK-BAT-001/OPS009/UI251/SS331341343; no DB timestamp-derived cutoff or administrative lookup.
 */
@NullMarked
@FunctionalInterface
public interface SuccessRunLookup {
  BatchRun resolve(UUID priorId, Instant observed) throws IOException;
}
