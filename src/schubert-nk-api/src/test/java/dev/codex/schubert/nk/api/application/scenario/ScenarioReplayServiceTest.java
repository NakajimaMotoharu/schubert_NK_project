package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.FILE;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.HASH;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.LAYOUTS;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.PATH;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.decrypt;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.encrypt;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.key;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.metadata;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.newContext;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.request;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.typed;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioReplayFixture.wire;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListResponseData;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** SS324 §6.3/SSC-026, UI232/234/237, PT-SCN-009-S01..S05. No DB/file/current auth claim. */
final class ScenarioReplayServiceTest {
  private static final String FIXTURE_SCN_F30DFFA3 = "SCN";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_20260908090001123_E5C758D8 = "20260908090001123";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_20260908090002789_D269B2BC = "20260908090002789";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_GAM_5BC4EFCF = "GAM";
  private static final String FIXTURE_SCNRSP01_DD42C8D5 = "SCNRSP01";
  private static final String FIXTURE_READY_6630F9C3 = ".ready";
  private static final String FIXTURE_20260909_291418E8 = "20260909/";
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(101, "reader", Role.USER);
  private static final AuthenticatedActor OTHER = new AuthenticatedActor(102, "other", Role.ADMIN);
  private static final UUID RESPONSE = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final UUID NEXT = UUID.fromString("00000000-0000-4000-8000-000000000002");
  private static final Instant COMPLETED = Instant.parse("2026-09-08T00:00:01.123456789Z");
  private static final Instant SENT = Instant.parse("2026-09-08T00:00:02.789123456Z");

  @Test
  void sixResponsesAndInlineMaximumMatchIndependentWireAndCrypto() throws Exception {
    try (var codec = codec()) {
      var service = new ScenarioReplayService(codec);
      for (String prefix : LAYOUTS) {
        for (int count : prefix.equals(FIXTURE_SCN_F30DFFA3) ? List.of(0, 1, 200) : List.of(0)) {
          var request = request(prefix);
          assertEquals(prefix + "RSP01", request.responseLayoutId().value());
          var completion =
              service.captureSuccess(
                  request, ACTOR, typed(prefix, false, count), RESPONSE, COMPLETED);
          assertEquals(InboxCompletionState.COMPLETED, completion.state());
          assertEquals(InboxResultReference.none(), completion.resultReference());
          assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), completion.completedAt());
          assertEquals(prefix + "RSP01", completion.responseLayoutId());
          assertEquals(FIXTURE_001_A3FEAA64, completion.responseVersion());
          byte[] expected =
              wire(
                  prefix,
                  request.header().messageId(),
                  RESPONSE,
                  FIXTURE_20260908090001123_E5C758D8,
                  "b".repeat(64),
                  FIXTURE_0000_876EEFE0,
                  false,
                  count);
          assertArrayEquals(
              expected, decrypt(request, completion.responseSnapshot().orElseThrow()));
          var snapshot = service.read(request, ACTOR, completion);
          assertEquals(ResultCode.SUCCESS, snapshot.resultCode());
          assertEquals(prefix.equals(FIXTURE_SCN_F30DFFA3), snapshot.detail().isPresent());
          assertTrue(snapshot.descriptor().isEmpty());
          assertEquals("ScenarioSnapshot[REDACTED]", snapshot.toString());
          for (boolean replay : List.of(false, true))
            assertArrayEquals(
                wire(
                    prefix,
                    request.header().messageId(),
                    NEXT,
                    FIXTURE_20260908090002789_D269B2BC,
                    "b".repeat(64),
                    replay ? FIXTURE_0200_FC9DB3AC : FIXTURE_0000_876EEFE0,
                    false,
                    count),
                service.reply(snapshot, request, ACTOR, NEXT, SENT, replay));
          if (prefix.equals(FIXTURE_SCN_F30DFFA3) || prefix.equals(FIXTURE_GAM_5BC4EFCF)) {
            var current = newContext(request);
            assertArrayEquals(
                wire(
                    prefix,
                    request.header().messageId(),
                    NEXT,
                    FIXTURE_20260908090002789_D269B2BC,
                    "d".repeat(64),
                    FIXTURE_0200_FC9DB3AC,
                    false,
                    count),
                service.reply(snapshot, current, ACTOR, NEXT, SENT, true));
          }
        }
      }
    }
  }

  @Test
  void fileMetadataAndDefiniteErrorsKeepExactReferencesAndCodes() throws Exception {
    try (var codec = codec()) {
      var service = new ScenarioReplayService(codec);
      for (int count : List.of(201, 10_000)) {
        var request = request(FIXTURE_SCN_F30DFFA3);
        var completion =
            service.captureSuccess(
                request, ACTOR, typed(FIXTURE_SCN_F30DFFA3, true, count), RESPONSE, COMPLETED);
        assertEquals(
            InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 30),
            completion.resultReference());
        assertArrayEquals(
            wire(
                FIXTURE_SCN_F30DFFA3,
                request.header().messageId(),
                RESPONSE,
                FIXTURE_20260908090001123_E5C758D8,
                "b".repeat(64),
                FIXTURE_0000_876EEFE0,
                true,
                count),
            decrypt(request, completion.responseSnapshot().orElseThrow()));
        var saved = service.read(request, ACTOR, completion);
        var descriptor = saved.descriptor().orElseThrow();
        assertEquals(FILE, descriptor.fileId());
        assertEquals(PATH, descriptor.relativePath());
        assertEquals(HASH, descriptor.sha256());
        assertEquals(4800L * count, descriptor.byteLength());
        assertEquals(4800, descriptor.recordLength());
        assertEquals(count, descriptor.recordCount());
        assertEquals(30, saved.detail().orElseThrow().scriptFileId().value());
        assertArrayEquals(
            wire(
                FIXTURE_SCN_F30DFFA3,
                request.header().messageId(),
                NEXT,
                FIXTURE_20260908090002789_D269B2BC,
                "b".repeat(64),
                FIXTURE_0200_FC9DB3AC,
                true,
                count),
            service.reply(saved, request, ACTOR, NEXT, SENT, true));
      }
      for (String prefix : LAYOUTS) {
        var request = request(prefix);
        for (ResultCode code :
            prefix.equals(FIXTURE_SCN_F30DFFA3)
                ? List.of(ResultCode.RESOURCE_LIMIT, ResultCode.NOT_FOUND)
                : List.of(ResultCode.RESOURCE_LIMIT)) {
          String expectedCode = code == ResultCode.RESOURCE_LIMIT ? "9001" : "0104";
          var completion = service.captureFailure(request, ACTOR, code, RESPONSE, COMPLETED);
          assertEquals(InboxCompletionState.ERROR, completion.state());
          assertEquals(InboxResultReference.none(), completion.resultReference());
          assertArrayEquals(
              wire(
                  prefix,
                  request.header().messageId(),
                  RESPONSE,
                  FIXTURE_20260908090001123_E5C758D8,
                  "b".repeat(64),
                  expectedCode,
                  false,
                  0),
              decrypt(request, completion.responseSnapshot().orElseThrow()));
          var snapshot = service.read(request, ACTOR, completion);
          assertEquals(code, snapshot.resultCode());
          assertTrue(snapshot.detail().isEmpty());
          assertTrue(snapshot.descriptor().isEmpty());
          for (boolean replay : List.of(false, true))
            assertArrayEquals(
                wire(
                    prefix,
                    request.header().messageId(),
                    NEXT,
                    FIXTURE_20260908090002789_D269B2BC,
                    "b".repeat(64),
                    expectedCode,
                    false,
                    0),
                service.reply(snapshot, request, ACTOR, NEXT, SENT, replay));
          assertArrayEquals(
              wire(
                  prefix,
                  request.header().messageId(),
                  NEXT,
                  FIXTURE_20260908090002789_D269B2BC,
                  "b".repeat(64),
                  expectedCode,
                  false,
                  0),
              service.failure(request, code, NEXT, SENT));
        }
        for (ResultCode code : List.of(ResultCode.SESSION_INVALID, ResultCode.TEMPORARY_FAILURE)) {
          assertArrayEquals(
              wire(
                  prefix,
                  request.header().messageId(),
                  NEXT,
                  FIXTURE_20260908090002789_D269B2BC,
                  "b".repeat(64),
                  code == ResultCode.SESSION_INVALID ? "0102" : "9000",
                  false,
                  0),
              service.failure(request, code, NEXT, SENT));
        }
      }
    }
  }

  @Test
  void authenticatedTamperingAndIdentityMixupsAreNeverReplayed() throws Exception {
    try (var codec = codec()) {
      var service = new ScenarioReplayService(codec);
      var request = request(FIXTURE_SCN_F30DFFA3);
      byte[] good =
          wire(
              FIXTURE_SCN_F30DFFA3,
              request.header().messageId(),
              RESPONSE,
              FIXTURE_20260908090001123_E5C758D8,
              "b".repeat(64),
              FIXTURE_0000_876EEFE0,
              false,
              1);
      var completion =
          completion(request, good, InboxCompletionState.COMPLETED, InboxResultReference.none());
      assertEquals(ResultCode.SUCCESS, service.read(request, ACTOR, completion).resultCode());
      // Every mutation is independently re-encrypted: GCM success must not bypass semantic
      // validation.
      Object[][] corruptions = {
        {0, "BADPROTO"},
        {8, "002"},
        {11, "GAMRSP01"},
        {19, "002"},
        {22, "R"},
        {23, "A"},
        {24, "not-a-uuid"},
        {60, NEXT.toString()},
        {96, "20260908090002123"},
        {113, "!"},
        {177, "0255"},
        {181, "001727"},
        {187, "004799"},
        {193, "000002"},
        {199, "000000256"},
        {208, FIXTURE_0200_FC9DB3AC},
        {212, "X"},
        {256, "000000000031"},
        {268, "UNKNOWN   "},
        {256 + 1328, "F"},
        {256 + 1712, "X"},
        {256 + 1728, "000000000000"},
        {256 + 1728 + 26, "unknown"},
        {256 + 1728 + 4787, "X"}
      };
      for (Object[] mutation : corruptions) {
        byte[] changed = good.clone();
        put(changed, (int) mutation[0], (String) mutation[1]);
        var bad =
            completion(
                request, changed, InboxCompletionState.COMPLETED, InboxResultReference.none());
        denied(() -> service.read(request, ACTOR, bad));
      }
      for (byte[] changed :
          List.of(
              Arrays.copyOf(good, good.length - 1),
              Arrays.copyOf(good, good.length + 1),
              new byte[0])) {
        var bad =
            completion(
                request, changed, InboxCompletionState.COMPLETED, InboxResultReference.none());
        denied(() -> service.read(request, ACTOR, bad));
      }
      for (var bad :
          List.of(
              replace(
                  completion,
                  InboxCompletionState.ERROR,
                  completion.resultReference(),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  completion.responseSnapshot(),
                  completion.completedAt()),
              replace(
                  completion,
                  completion.state(),
                  InboxResultReference.authSession(FILE),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  completion.responseSnapshot(),
                  completion.completedAt()),
              replace(
                  completion,
                  completion.state(),
                  completion.resultReference(),
                  "GAMRSP01",
                  FIXTURE_001_A3FEAA64,
                  completion.responseSnapshot(),
                  completion.completedAt()),
              replace(
                  completion,
                  completion.state(),
                  completion.resultReference(),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  "002",
                  completion.responseSnapshot(),
                  completion.completedAt()),
              replace(
                  completion,
                  completion.state(),
                  completion.resultReference(),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  Optional.empty(),
                  completion.completedAt()),
              replace(
                  completion,
                  completion.state(),
                  completion.resultReference(),
                  FIXTURE_SCNRSP01_DD42C8D5,
                  FIXTURE_001_A3FEAA64,
                  completion.responseSnapshot(),
                  SENT))) {
        denied(() -> service.read(request, ACTOR, bad));
      }
      byte[] tag = completion.responseSnapshot().orElseThrow().ciphertext();
      tag[tag.length - 1] ^= 1;
      for (var encrypted :
          List.of(
              new EncryptedResponseSnapshot("fixture", tag),
              new EncryptedResponseSnapshot(
                  "unknown", completion.responseSnapshot().orElseThrow().ciphertext()))) {
        var bad =
            replace(
                completion,
                completion.state(),
                completion.resultReference(),
                FIXTURE_SCNRSP01_DD42C8D5,
                FIXTURE_001_A3FEAA64,
                Optional.of(encrypted),
                completion.completedAt());
        denied(() -> service.read(request, ACTOR, bad));
      }
      denied(() -> service.read(request, OTHER, completion));
      denied(() -> service.read(request(FIXTURE_SCN_F30DFFA3), ACTOR, completion));
      var saved = service.read(request, ACTOR, completion);
      denied(() -> service.reply(saved, request, OTHER, NEXT, SENT, true));
      denied(() -> service.reply(saved, request(FIXTURE_SCN_F30DFFA3), ACTOR, NEXT, SENT, true));
      denied(() -> service.reply(saved, request(FIXTURE_GAM_5BC4EFCF), ACTOR, NEXT, SENT, true));
      byte[] file =
          wire(
              FIXTURE_SCN_F30DFFA3,
              request.header().messageId(),
              RESPONSE,
              FIXTURE_20260908090001123_E5C758D8,
              "b".repeat(64),
              FIXTURE_0000_876EEFE0,
              true,
              201);
      for (Object[] mutation :
          new Object[][] {
            {1329, NEXT.toString()},
            {1365, "20260230/"},
            {1365, "20260908/00000000-0000-4000-8000-000000000124.ready"},
            {1621, "000000964801"},
            {1633, "G"},
            {1697, "004799"},
            {1703, "000010001"},
            {1703, "000000000"}
          }) {
        byte[] changed = file.clone();
        put(changed, 256 + (int) mutation[0], (String) mutation[1]);
        var bad =
            completion(
                request,
                changed,
                InboxCompletionState.COMPLETED,
                InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 30));
        denied(() -> service.read(request, ACTOR, bad));
      }
      var missingReference =
          completion(request, file, InboxCompletionState.COMPLETED, InboxResultReference.none());
      denied(() -> service.read(request, ACTOR, missingReference));
      for (String prefix : LAYOUTS) {
        var current = request(prefix);
        for (String code : List.of("0102", "9000", "0104", "9001")) {
          byte[] error =
              wire(
                  prefix,
                  current.header().messageId(),
                  RESPONSE,
                  FIXTURE_20260908090001123_E5C758D8,
                  "b".repeat(64),
                  code,
                  false,
                  0);
          if (code.equals("9001") || code.equals("0104") && prefix.equals(FIXTURE_SCN_F30DFFA3)) {
            var bad =
                completion(
                    current, error, InboxCompletionState.COMPLETED, InboxResultReference.none());
            denied(() -> service.read(current, ACTOR, bad));
          } else {
            var bad =
                completion(current, error, InboxCompletionState.ERROR, InboxResultReference.none());
            denied(() -> service.read(current, ACTOR, bad));
          }
        }
      }
    }
  }

  @Test
  void nullInvalidCaptureAndClosedKeysPreserveBoundaries() throws Exception {
    assertThrows(NullPointerException.class, () -> new ScenarioReplayService(null));
    var codec = codec();
    try {
      var service = new ScenarioReplayService(codec);
      var request = request(FIXTURE_SCN_F30DFFA3);
      var response = typed(FIXTURE_SCN_F30DFFA3, false, 0);
      var completion = service.captureSuccess(request, ACTOR, response, RESPONSE, COMPLETED);
      var saved = service.read(request, ACTOR, completion);
      List<Executable> nulls =
          List.of(
              () -> service.captureSuccess(null, ACTOR, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, null, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, null, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, response, null, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, response, RESPONSE, null),
              () ->
                  service.captureFailure(
                      null, ACTOR, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(
                      request, null, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ACTOR, null, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(
                      request, ACTOR, ResultCode.RESOURCE_LIMIT, null, COMPLETED),
              () ->
                  service.captureFailure(request, ACTOR, ResultCode.RESOURCE_LIMIT, RESPONSE, null),
              () -> service.read(null, ACTOR, completion),
              () -> service.read(request, null, completion),
              () -> service.read(request, ACTOR, null),
              () -> service.reply(null, request, ACTOR, NEXT, SENT, true),
              () -> service.reply(saved, null, ACTOR, NEXT, SENT, true),
              () -> service.reply(saved, request, null, NEXT, SENT, true),
              () -> service.reply(saved, request, ACTOR, null, SENT, true),
              () -> service.reply(saved, request, ACTOR, NEXT, null, true),
              () -> service.failure(null, ResultCode.TEMPORARY_FAILURE, NEXT, SENT),
              () -> service.failure(request, null, NEXT, SENT),
              () -> service.failure(request, ResultCode.TEMPORARY_FAILURE, null, SENT),
              () -> service.failure(request, ResultCode.TEMPORARY_FAILURE, NEXT, null));
      for (var call : nulls) assertThrows(NullPointerException.class, call);
      for (var invalid :
          List.of(
              typed(FIXTURE_GAM_5BC4EFCF, false, 0),
              new TypedPayloadValues(
                  new LayoutId(FIXTURE_SCNRSP01_DD42C8D5), new GameListResponseData(0), List.of()),
              new TypedPayloadValues(
                  new LayoutId(FIXTURE_SCNRSP01_DD42C8D5), metadata(31, false, 0, PATH), List.of()),
              new TypedPayloadValues(
                  new LayoutId(FIXTURE_SCNRSP01_DD42C8D5),
                  metadata(30, true, 201, "20260230/" + FILE + FIXTURE_READY_6630F9C3),
                  List.of()),
              typed(FIXTURE_SCN_F30DFFA3, false, 201)))
        denied(() -> service.captureSuccess(request, ACTOR, invalid, RESPONSE, COMPLETED));
      for (ResultCode code : ResultCode.values()) {
        if (code != ResultCode.RESOURCE_LIMIT && code != ResultCode.NOT_FOUND)
          denied(() -> service.captureFailure(request, ACTOR, code, RESPONSE, COMPLETED));
        if (code != ResultCode.RESOURCE_LIMIT
            && code != ResultCode.NOT_FOUND
            && code != ResultCode.SESSION_INVALID
            && code != ResultCode.TEMPORARY_FAILURE)
          denied(() -> service.failure(request, code, NEXT, SENT));
      }
      var games = request(FIXTURE_GAM_5BC4EFCF);
      denied(() -> service.captureFailure(games, ACTOR, ResultCode.NOT_FOUND, RESPONSE, COMPLETED));
      denied(() -> service.failure(games, ResultCode.NOT_FOUND, NEXT, SENT));
      for (Instant invalid : List.of(Instant.parse("+10000-01-01T00:00:00Z"), Instant.MAX)) {
        denied(() -> service.captureSuccess(request, ACTOR, response, RESPONSE, invalid));
        denied(
            () ->
                service.captureFailure(
                    request, ACTOR, ResultCode.RESOURCE_LIMIT, RESPONSE, invalid));
        denied(() -> service.reply(saved, request, ACTOR, NEXT, invalid, true));
        denied(() -> service.failure(request, ResultCode.TEMPORARY_FAILURE, NEXT, invalid));
      }
      codec.close();
      denied(() -> service.captureSuccess(request, ACTOR, response, RESPONSE, COMPLETED));
      denied(
          () ->
              service.captureFailure(
                  request, ACTOR, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED));
      denied(() -> service.read(request, ACTOR, completion));
    } finally {
      codec.close();
    }
  }

  @Test
  void oneHundredConcurrentRebuildsDoNotMutateFrozenResults() throws Exception {
    try (var codec = codec();
        var workers = Executors.newFixedThreadPool(16)) {
      var service = new ScenarioReplayService(codec);
      var request = request(FIXTURE_SCN_F30DFFA3);
      var completion =
          service.captureSuccess(
              request, ACTOR, typed(FIXTURE_SCN_F30DFFA3, false, 1), RESPONSE, COMPLETED);
      byte[] original = completion.responseSnapshot().orElseThrow().ciphertext();
      List<Future<?>> results = new ArrayList<>();
      var start = new CountDownLatch(1);
      for (int i = 0; i < 100; i++) {
        final int index = i;
        results.add(
            workers.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  var saved = service.read(request, ACTOR, completion);
                  UUID id = new UUID(1, index + 1);
                  assertArrayEquals(
                      wire(
                          FIXTURE_SCN_F30DFFA3,
                          request.header().messageId(),
                          id,
                          FIXTURE_20260908090002789_D269B2BC,
                          "b".repeat(64),
                          FIXTURE_0200_FC9DB3AC,
                          false,
                          1),
                      service.reply(saved, request, ACTOR, id, SENT, true));
                  return null;
                }));
      }
      start.countDown();
      for (var result : results) result.get(20, TimeUnit.SECONDS);
      assertArrayEquals(original, completion.responseSnapshot().orElseThrow().ciphertext());
      assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), completion.completedAt());
      assertEquals(InboxResultReference.none(), completion.resultReference());
    }
  }

  /** PT-SCN-009-S06: only descriptor UUID/path changes, not the captured header or lifetime. */
  @Test
  void regeneratedDescriptorKeepsOriginalHeaderResultAndCompletionTime() throws Exception {
    try (var codec = codec()) {
      var service = new ScenarioReplayService(codec);
      var request = request(FIXTURE_SCN_F30DFFA3);
      var original =
          service.captureSuccess(
              request, ACTOR, typed(FIXTURE_SCN_F30DFFA3, true, 201), RESPONSE, COMPLETED);
      byte[] oldCiphertext = original.responseSnapshot().orElseThrow().ciphertext();
      var replacement =
          new LargeResultDescriptor(
              NEXT, FIXTURE_20260909_291418E8 + NEXT + FIXTURE_READY_6630F9C3, 964800, HASH, 201);
      var updated = service.replaceFile(newContext(request), ACTOR, original, replacement);
      byte[] expected =
          wire(
              FIXTURE_SCN_F30DFFA3,
              request.header().messageId(),
              RESPONSE,
              FIXTURE_20260908090001123_E5C758D8,
              "b".repeat(64),
              FIXTURE_0000_876EEFE0,
              true,
              201);
      put(expected, 256 + 1329, NEXT.toString());
      put(expected, 256 + 1365, FIXTURE_20260909_291418E8 + NEXT + FIXTURE_READY_6630F9C3);
      assertArrayEquals(expected, decrypt(request, updated.responseSnapshot().orElseThrow()));
      assertArrayEquals(oldCiphertext, original.responseSnapshot().orElseThrow().ciphertext());
      assertEquals(original.completedAt(), updated.completedAt());
      assertEquals(original.state(), updated.state());
      assertEquals(original.resultReference(), updated.resultReference());
      assertEquals(FIXTURE_SCNRSP01_DD42C8D5, updated.responseLayoutId());
      assertEquals(FIXTURE_001_A3FEAA64, updated.responseVersion());
      var saved = service.read(request, ACTOR, updated);
      assertEquals(NEXT, saved.descriptor().orElseThrow().fileId());
      put(expected, 24, NEXT.toString());
      put(expected, 96, FIXTURE_20260908090002789_D269B2BC);
      put(expected, 208, FIXTURE_0200_FC9DB3AC);
      assertArrayEquals(expected, service.reply(saved, request, ACTOR, NEXT, SENT, true));
      assertThrows(
          NullPointerException.class,
          () -> service.replaceFile(null, ACTOR, original, replacement));
      assertThrows(
          NullPointerException.class,
          () -> service.replaceFile(request, null, original, replacement));
      assertThrows(
          NullPointerException.class, () -> service.replaceFile(request, ACTOR, null, replacement));
      assertThrows(
          NullPointerException.class, () -> service.replaceFile(request, ACTOR, original, null));
      denied(() -> service.replaceFile(request, OTHER, original, replacement));
      for (var wrong :
          List.of(
              new LargeResultDescriptor(
                  NEXT, FIXTURE_20260909_291418E8 + NEXT + FIXTURE_READY_6630F9C3, 4800, HASH, 1),
              new LargeResultDescriptor(
                  NEXT,
                  FIXTURE_20260909_291418E8 + NEXT + FIXTURE_READY_6630F9C3,
                  964800,
                  "0".repeat(64),
                  201))) denied(() -> service.replaceFile(request, ACTOR, original, wrong));
      var inline =
          service.captureSuccess(
              request, ACTOR, typed(FIXTURE_SCN_F30DFFA3, false, 0), RESPONSE, COMPLETED);
      denied(() -> service.replaceFile(request, ACTOR, inline, replacement));
    }
  }

  private static ResponseSnapshotCodec codec() {
    return new ResponseSnapshotCodec("fixture", key(), null, null);
  }

  private static InboxCompletion completion(
      ScenarioRequest request,
      byte[] body,
      InboxCompletionState state,
      InboxResultReference reference)
      throws Exception {
    return new InboxCompletion(
        state,
        reference,
        request.responseLayoutId().value(),
        FIXTURE_001_A3FEAA64,
        Optional.of(encrypt(request, body)),
        COMPLETED.truncatedTo(ChronoUnit.MICROS));
  }

  private static InboxCompletion replace(
      InboxCompletion ignored,
      InboxCompletionState state,
      InboxResultReference reference,
      String layout,
      String version,
      Optional<EncryptedResponseSnapshot> encrypted,
      Instant completed) {
    return new InboxCompletion(state, reference, layout, version, encrypted, completed);
  }

  private static void denied(Executable action) {
    var failure = assertThrows(TemporaryInfrastructureException.class, action);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
