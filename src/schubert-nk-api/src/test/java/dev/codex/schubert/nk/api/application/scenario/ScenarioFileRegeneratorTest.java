package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.FILE;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.HASH;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.PATH;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.encrypt;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.key;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.metadata;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.number;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.request;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.typed;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.wire;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.spaces;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.ProviderException;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/**
 * PT-SCN-009-F01..F03: independent record offsets/hash, immutable metadata and call side effects.
 */
final class ScenarioFileRegeneratorTest {
  private static final String FIXTURE_SCN_F30DFFA3 = "SCN";
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(101, "reader", Role.USER);
  private static final Instant TIME = Instant.parse("2026-09-08T00:00:01.123Z");
  private static final UUID NEW_FILE = UUID.fromString("00000000-0000-4000-8000-000000000456");

  @Test
  void originalContentRegeneratesAtAllFileBoundaries() throws Exception {
    try (var keys = new ResponseSnapshotCodec("fixture", key(), null, null)) {
      var responses = new ScenarioReplayService(keys);
      for (int count : List.of(1, 201, 10_000)) {
        String hash = independentHash(count);
        var saved = saved(responses, count, hash);
        var current = current(count, metadata(30, false, 0, PATH));
        var calls = new AtomicInteger();
        var regenerated = descriptor(count, hash);
        var subject =
            new ScenarioFileRegenerator(
                (records, time) -> {
                  assertEquals(current.records(), records);
                  assertEquals(TIME.plusSeconds(86400), time);
                  assertThrows(UnsupportedOperationException.class, () -> records.clear());
                  assertEquals(1, calls.incrementAndGet());
                  return regenerated;
                });
        assertSame(regenerated, subject.regenerate(saved, current, TIME.plusSeconds(86400)));
        assertEquals(1, calls.get());
        assertEquals(FILE, saved.descriptor().orElseThrow().fileId());
        assertEquals(hash, saved.descriptor().orElseThrow().sha256());
        assertEquals(NEW_FILE, regenerated.fileId());
        assertTrue(
            ScenarioFileRegenerator.sameContent(saved.descriptor().orElseThrow(), regenerated));
        assertEquals(4800L * count, regenerated.byteLength());
      }
    }
  }

  @Test
  void changedMasterAndUnexpectedPublishedContentAreRejected() throws Exception {
    try (var keys = new ResponseSnapshotCodec("fixture", key(), null, null)) {
      var responses = new ScenarioReplayService(keys);
      String hash = independentHash(1);
      var saved = saved(responses, 1, hash, true);
      var calls = new AtomicInteger();
      var subject =
          new ScenarioFileRegenerator(
              (records, time) -> {
                calls.incrementAndGet();
                return descriptor(records.size(), hash);
              });
      for (int field = 0; field < 8; field++) {
        var changed = current(1, changedMetadata(field));
        denied(() -> subject.regenerate(saved, changed, TIME));
      }
      for (int count : List.of(0, 2)) {
        var changed = current(count, changedMetadata(-1));
        denied(() -> subject.regenerate(saved, changed, TIME));
      }
      var original = current(1, changedMetadata(-1));
      var changedBody =
          new ScenarioDetailSnapshot(
              original.metadata(),
              List.of(
                  new ScenarioEntryRecord(
                      new EntryId(1),
                      1,
                      1,
                      EntryType.NARRATION,
                      Optional.empty(),
                      "changed",
                      0,
                      Optional.empty(),
                      Optional.empty())));
      denied(() -> subject.regenerate(saved, changedBody, TIME));
      for (int i = 0; i < 32; i++) {
        byte[] different = HexFormat.of().parseHex(hash);
        different[i] ^= 1;
        var bad = saved(responses, 1, HexFormat.of().formatHex(different), true);
        denied(() -> subject.regenerate(bad, original, TIME));
      }
      assertEquals(0, calls.get(), "master mismatch must precede publication");
      for (var bad : List.of(descriptor(2, hash), descriptor(1, "0".repeat(64)))) {
        var wrongPublisher =
            new ScenarioFileRegenerator(
                (records, time) -> {
                  calls.incrementAndGet();
                  return bad;
                });
        denied(() -> wrongPublisher.regenerate(saved, original, TIME));
      }
      assertEquals(2, calls.get(), "each failed publication is attempted only once");
    }
  }

  @Test
  void nullErrorsAndProviderFailuresPreserveBoundaries() throws Exception {
    ScenarioFilePublisher unused = (records, time) -> fail("publication was not allowed");
    assertThrows(NullPointerException.class, () -> new ScenarioFileRegenerator(null));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioFileRegenerator(null, () -> MessageDigest.getInstance("SHA-256")));
    assertThrows(NullPointerException.class, () -> new ScenarioFileRegenerator(unused, null));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioFileRegenerator.sameContent(null, descriptor(1, HASH)));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioFileRegenerator.sameContent(descriptor(1, HASH), null));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioDetailDelivery.fileResponse(null, descriptor(1, HASH)));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioDetailDelivery.fileResponse(metadata(30, false, 0, PATH), null));
    try (var keys = new ResponseSnapshotCodec("fixture", key(), null, null)) {
      var responses = new ScenarioReplayService(keys);
      var saved = saved(responses, 1, independentHash(1));
      var current = current(1, metadata(30, false, 0, PATH));
      var subject = new ScenarioFileRegenerator(unused);
      assertThrows(NullPointerException.class, () -> subject.regenerate(null, current, TIME));
      assertThrows(NullPointerException.class, () -> subject.regenerate(saved, null, TIME));
      assertThrows(NullPointerException.class, () -> subject.regenerate(saved, current, null));
      var request = request(FIXTURE_SCN_F30DFFA3);
      for (var other :
          List.of(
              responses.captureSuccess(
                  request, ACTOR, typed(FIXTURE_SCN_F30DFFA3, false, 1), FILE, TIME),
              responses.captureFailure(request, ACTOR, ResultCode.NOT_FOUND, FILE, TIME))) {
        var invalid = responses.read(request, ACTOR, other);
        denied(() -> subject.regenerate(invalid, current, TIME));
      }
      var cryptoFailure =
          new ScenarioFileRegenerator(
              unused,
              () -> {
                throw new NoSuchAlgorithmException("synthetic confidential provider text");
              });
      denied(() -> cryptoFailure.regenerate(saved, current, TIME));
      byte[][] retainedBuffer = new byte[1][];
      var providerFailure =
          new ScenarioFileRegenerator(
              unused,
              () ->
                  new MessageDigest("SHA-256") {
                    @Override
                    protected void engineUpdate(byte input) {
                      fail("unexpected single-byte update");
                    }

                    @Override
                    protected void engineUpdate(byte[] input, int offset, int length) {
                      retainedBuffer[0] = input;
                      throw new ProviderException("synthetic confidential digest failure");
                    }

                    @Override
                    protected byte[] engineDigest() {
                      return fail("digest after failed update");
                    }

                    @Override
                    protected void engineReset() {
                      fail("unexpected reset");
                    }
                  });
      denied(() -> providerFailure.regenerate(saved, current, TIME));
      assertNotNull(retainedBuffer[0]);
      assertArrayEquals(new byte[4800], retainedBuffer[0]);
      var nullDigest = new ScenarioFileRegenerator(unused, () -> null);
      assertThrows(NullPointerException.class, () -> nullDigest.regenerate(saved, current, TIME));
      for (ScenarioFilePublisher faulty :
          List.<ScenarioFilePublisher>of(
              (records, time) -> {
                throw new CapacityExceededException();
              },
              (records, time) -> {
                throw new IOException("synthetic confidential path");
              },
              (records, time) -> {
                throw new IllegalArgumentException("synthetic confidential metadata");
              },
              (records, time) -> {
                throw new IllegalStateException("synthetic confidential state");
              })) {
        var fails = new ScenarioFileRegenerator(faulty);
        denied(() -> fails.regenerate(saved, current, TIME));
      }
      var nullPublisher = new ScenarioFileRegenerator((records, time) -> null);
      assertThrows(
          NullPointerException.class, () -> nullPublisher.regenerate(saved, current, TIME));
    }
  }

  private static ScenarioDetailSnapshot current(int count, ScenarioDetailResponseData metadata) {
    return new ScenarioDetailSnapshot(
        metadata,
        typed(FIXTURE_SCN_F30DFFA3, false, count).records().stream()
            .map(ScenarioEntryRecord.class::cast)
            .toList());
  }

  private static LargeResultDescriptor descriptor(int count, String hash) {
    return new LargeResultDescriptor(
        NEW_FILE, "20260909/" + NEW_FILE + ".ready", 4800L * count, hash, count);
  }

  private static ScenarioReplayService.Snapshot saved(
      ScenarioReplayService responses, int count, String hash) throws Exception {
    return saved(responses, count, hash, false);
  }

  private static ScenarioReplayService.Snapshot saved(
      ScenarioReplayService responses, int count, String hash, boolean navigation)
      throws Exception {
    var request = request(FIXTURE_SCN_F30DFFA3);
    byte[] wire =
        wire(
            FIXTURE_SCN_F30DFFA3,
            request.header().messageId(),
            FILE,
            "20260908090001123",
            "b".repeat(64),
            "0000",
            true,
            count);
    put(wire, 256 + 1633, hash);
    if (navigation) {
      put(wire, 256 + 792, "20");
      put(wire, 256 + 804, "Previous");
      put(wire, 256 + 1060, "40");
      put(wire, 256 + 1072, "Next");
    }
    return responses.read(
        request,
        ACTOR,
        new InboxCompletion(
            InboxCompletionState.COMPLETED,
            InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 30),
            "SCNRSP01",
            "001",
            Optional.of(encrypt(request, wire)),
            TIME));
  }

  private static ScenarioDetailResponseData changedMetadata(int field) {
    return new ScenarioDetailResponseData(
        new ScriptFileId(field == 0 ? 31 : 30),
        field == 1 ? GameCode.NUKITASHI_2 : GameCode.NUKITASHI_1,
        field == 2 ? "Changed" : "Chapter",
        DisplayPath.of(field == 3 ? "scenario/02.txt" : "scenario/01.txt"),
        Optional.of(new ScriptFileId(field == 4 ? 21 : 20)),
        Optional.of(field == 5 ? "Changed" : "Previous"),
        Optional.of(new ScriptFileId(field == 6 ? 41 : 40)),
        Optional.of(field == 7 ? "Changed" : "Next"),
        DeliveryMode.INLINE,
        Optional.empty(),
        Optional.empty(),
        0,
        Optional.empty(),
        0,
        0);
  }

  /**
   * Literal UI234 record fields only; neither producer encoder nor regenerator computes expected.
   */
  private static String independentHash(int count) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    for (int i = 1; i <= count; i++) {
      byte[] record = spaces(4800);
      number(record, 0, 12, i);
      number(record, 12, 6, i);
      number(record, 18, 8, 1);
      put(record, 26, "narration");
      put(record, 164, "本文");
      number(record, 4260, 3, 0);
      digest.update(record);
    }
    return HexFormat.of().formatHex(digest.digest());
  }

  private static void denied(Executable action) {
    var failure = assertThrows(TemporaryInfrastructureException.class, action);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
