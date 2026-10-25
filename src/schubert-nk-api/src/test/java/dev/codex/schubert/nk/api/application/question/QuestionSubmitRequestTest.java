package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Literal UI236 offsets and independent SS323 section9.6 LP/JCE oracle. PG189/SSC070. */
final class QuestionSubmitRequestTest {
  private static final UUID TOKEN = new UUID(60, 1);
  private static final UUID MESSAGE = new UUID(70, 1);
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(1, "fixture", Role.USER);
  private static final Instant NOW = Instant.parse("2026-09-20T00:00:00Z");

  @Test
  @DisplayName("PT-QST-SUB001 literal wire and independent canonical HMAC")
  void literalWireAndCanonical() throws Exception {
    var wire = wire(data("公開fixture", TOKEN), MESSAGE);
    try (var request = QuestionSubmitRequest.decode(wire)) {
      assertSame(wire.header(), request.header());
      assertEquals(TOKEN, request.operationToken());
      assertArrayEquals("公開fixture".toCharArray(), request.copyQuestion());
      check(request, ACTOR, "公開fixture");
    }
  }

  @Test
  @DisplayName("PT-QST-SUB002 exact byte and Unicode boundaries")
  void byteAndUnicodeBoundaries() throws Exception {
    for (String value :
        List.of("a", "a".repeat(4096), "é".repeat(2048), "😀".repeat(1024), " A", "a　")) {
      try (var request = QuestionSubmitRequest.decode(wire(data(value, TOKEN), MESSAGE))) {
        assertArrayEquals(value.toCharArray(), request.copyQuestion());
        check(request, ACTOR, value);
      }
    }
    for (String value : List.of("", "\r", "\n", "\t", "\0", "e\u0301"))
      invalid(wire(data(value, TOKEN), MESSAGE));
    byte[] malformed = data("a", TOKEN);
    malformed[0] = (byte) 0xc3;
    malformed[1] = 0x28;
    invalid(wire(malformed, MESSAGE));
    invalid(wire(Arrays.copyOf(data("a".repeat(4096), TOKEN), 4145), MESSAGE));
    // Fixed-width padding cannot retain a distinction between an input trailing space and padding.
    try (var request = QuestionSubmitRequest.decode(wire(data("a ", TOKEN), MESSAGE))) {
      assertArrayEquals(new char[] {'a'}, request.copyQuestion());
    }
  }

  @Test
  @DisplayName("PT-QST-SUB003 protocol, reserved and token rejection")
  void protocolRejection() {
    byte[] good = data("public", TOKEN);
    invalid(message("LOGREQ01", 1, InteractionKind.ASYNC_ACCEPTANCE, good, 0, 0, MESSAGE, "b"));
    assertThrows(
        dev.codex.schubert.nk.protocol.layout.LayoutValidationException.class,
        () -> message("QSBREQ01", 2, InteractionKind.ASYNC_ACCEPTANCE, good, 0, 0, MESSAGE, "b"));
    assertThrows(
        dev.codex.schubert.nk.protocol.layout.LayoutValidationException.class,
        () -> message("QSBREQ01", 1, InteractionKind.INTERNAL, good, 0, 0, MESSAGE, "b"));
    invalid(message("QSBREQ01", 1, InteractionKind.SYNCHRONOUS, good, 0, 0, MESSAGE, "b"));
    invalid(wire(Arrays.copyOf(good, 4143), MESSAGE));
    invalid(message("QSBREQ01", 1, InteractionKind.ASYNC_ACCEPTANCE, good, 1, 1, MESSAGE, "b"));
    for (int offset = 4132; offset < 4144; offset++) {
      byte[] changed = good.clone();
      changed[offset] = 'X';
      invalid(wire(changed, MESSAGE));
    }
    for (int offset : new int[] {4096, 4104, 4131}) {
      byte[] changed = good.clone();
      changed[offset] = 'Z';
      invalid(wire(changed, MESSAGE));
    }
  }

  @Test
  @DisplayName("PT-QST-SUB004 owner and body binding, metadata exclusion")
  void fingerprintBinding() throws Exception {
    try (var first = QuestionSubmitRequest.decode(wire(data("same", TOKEN), MESSAGE));
        var second =
            QuestionSubmitRequest.decode(
                message(
                    "QSBREQ01",
                    1,
                    InteractionKind.ASYNC_ACCEPTANCE,
                    data("same", new UUID(60, 2)),
                    0,
                    0,
                    new UUID(70, 2),
                    "c"));
        var changed = QuestionSubmitRequest.decode(wire(data("different", TOKEN), MESSAGE))) {
      assertArrayEquals(hash(first, ACTOR), hash(second, ACTOR));
      assertFalse(Arrays.equals(hash(first, ACTOR), hash(changed, ACTOR)));
      assertFalse(
          Arrays.equals(
              hash(first, ACTOR), hash(first, new AuthenticatedActor(2, "other", Role.ADMIN))));
      assertArrayEquals(
          hash(first, ACTOR), hash(first, new AuthenticatedActor(1, "renamed", Role.ADMIN)));
      check(second, ACTOR, "same");
    }
  }

  @Test
  @DisplayName("PT-QST-SUB005 independent buffers and terminal close")
  void ownershipAndClose() throws Exception {
    byte[] bytes = data("public", TOKEN);
    var request = QuestionSubmitRequest.decode(wire(bytes, MESSAGE));
    try {
      Arrays.fill(bytes, (byte) 'Z');
      char[] copy = request.copyQuestion();
      Arrays.fill(copy, 'X');
      assertArrayEquals("public".toCharArray(), request.copyQuestion());
      try (var first = request.canonical(ACTOR);
          var second = request.canonical(ACTOR)) {
        byte[] copied = first.fields().getFirst().value();
        assertNotNull(copied);
        Arrays.fill(copied, (byte) 'X');
        assertArrayEquals(
            "public".getBytes(StandardCharsets.UTF_8), first.fields().getFirst().value());
        request.close();
        request.close();
        assertArrayEquals(
            "public".getBytes(StandardCharsets.UTF_8), second.fields().getFirst().value());
      }
      for (org.junit.jupiter.api.function.Executable access :
          List.<org.junit.jupiter.api.function.Executable>of(
              request::header,
              request::operationToken,
              request::copyQuestion,
              () -> request.canonical(ACTOR)))
        assertEquals(
            "question submit request is closed",
            assertThrows(IllegalStateException.class, access).getMessage());
      assertEquals("QuestionSubmitRequest[REDACTED]", request.toString());
    } finally {
      request.close();
    }
    try (var fresh = QuestionSubmitRequest.decode(wire(data("public", TOKEN), MESSAGE))) {
      CanonicalRequest canonical = fresh.canonical(ACTOR);
      try {
        canonical.close();
        assertArrayEquals(new byte[6], canonical.fields().getFirst().value());
      } finally {
        canonical.close();
      }
      assertArrayEquals("public".toCharArray(), fresh.copyQuestion());
    }
  }

  @Test
  @DisplayName("PT-QST-SUB006 null contracts")
  void nullContracts() {
    assertThrows(NullPointerException.class, () -> QuestionSubmitRequest.decode(null));
    var request = QuestionSubmitRequest.decode(wire(data("public", TOKEN), MESSAGE));
    try {
      assertThrows(NullPointerException.class, () -> request.canonical(null));
      request.close();
      assertThrows(IllegalStateException.class, () -> request.canonical(null));
    } finally {
      request.close();
    }
  }

  @Test
  @DisplayName("PT-QST-SUB007 independent concurrent requests and atomic close")
  void concurrentScopes() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      List<Future<String>> results = new ArrayList<>();
      for (int i = 0; i < 64; i++) {
        final int index = i;
        results.add(
            executor.submit(
                () -> {
                  String value = "public-" + index;
                  try (var request =
                      QuestionSubmitRequest.decode(
                          wire(data(value, new UUID(60, index + 1)), MESSAGE))) {
                    check(request, ACTOR, value);
                    char[] copy = request.copyQuestion();
                    try {
                      return new String(copy);
                    } finally {
                      Arrays.fill(copy, '\0');
                    }
                  }
                }));
      }
      for (int i = 0; i < results.size(); i++)
        assertEquals("public-" + i, results.get(i).get(10, TimeUnit.SECONDS));
      var shared = QuestionSubmitRequest.decode(wire(data("shared", TOKEN), MESSAGE));
      try {
        synchronized (shared) {
          assertEquals(
              "shared",
              executor.submit(() -> new String(shared.copyQuestion())).get(5, TimeUnit.SECONDS));
        }
        var start = new CountDownLatch(1);
        var read =
            executor.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  try (var canonical = shared.canonical(ACTOR)) {
                    assertArrayEquals(
                        "shared".getBytes(StandardCharsets.UTF_8),
                        canonical.fields().getFirst().value());
                    return "complete";
                  } catch (IllegalStateException closed) {
                    assertEquals("question submit request is closed", closed.getMessage());
                    return "closed";
                  }
                });
        var close =
            executor.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  shared.close();
                  return true;
                });
        start.countDown();
        assertTrue(Set.of("complete", "closed").contains(read.get(5, TimeUnit.SECONDS)));
        assertTrue(close.get(5, TimeUnit.SECONDS));
        assertThrows(IllegalStateException.class, shared::copyQuestion);
      } finally {
        shared.close();
      }
    }
  }

  @Test
  @DisplayName("PT-QST-SUB008 redacted public evidence")
  void publicEvidenceAndRedaction() throws Exception {
    try (var request = QuestionSubmitRequest.decode(wire(data("public", TOKEN), MESSAGE));
        var canonical = request.canonical(ACTOR)) {
      assertEquals("QuestionSubmitRequest[REDACTED]", request.toString());
      assertFalse(canonical.toString().contains("public"));
      assertFalse(canonical.toString().contains(TOKEN.toString()));
      check(request, ACTOR, "public");
    }
    Path directory = Path.of("target/question-submit-traces");
    Files.createDirectories(directory);
    Files.writeString(
        directory.resolve("PT-QST-SUB008.txt"),
        "layout=QSBREQ01\ninteraction=A\ndataLength=4144\ncanonicalFieldCount=1\ncanonicalField=question/X1\ntarget=QUESTION:NEW\nmetadataExcluded=true\nrawBodySaved=false\n");
  }

  private static byte[] data(String body, UUID token) {
    byte[] bytes = new byte[4144];
    Arrays.fill(bytes, (byte) ' ');
    byte[] encoded = body.getBytes(StandardCharsets.UTF_8);
    if (encoded.length > 4096) throw new AssertionError("fixture overflow");
    System.arraycopy(encoded, 0, bytes, 0, encoded.length);
    byte[] id = token.toString().getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(id, 0, bytes, 4096, 36);
    return bytes;
  }

  private static WireMessage<FixedPayload> wire(byte[] bytes, UUID id) {
    return message("QSBREQ01", 1, InteractionKind.ASYNC_ACCEPTANCE, bytes, 0, 0, id, "b");
  }

  private static WireMessage<FixedPayload> message(
      String layout,
      int version,
      InteractionKind interaction,
      byte[] bytes,
      int recordLength,
      int recordCount,
      UUID id,
      String context) {
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            version,
            MessageKind.REQUEST,
            interaction,
            id,
            id,
            NOW.plusMillis(id.getLeastSignificantBits()),
            Optional.of(AuthenticationContext.of(context.repeat(64))),
            256,
            bytes.length,
            recordLength,
            recordCount,
            256 + bytes.length + recordLength * recordCount,
            Optional.empty());
    return new WireMessage<>(
        header,
        new FixedPayload(
            bytes, recordLength, recordCount == 0 ? List.of() : List.of(new byte[recordLength])));
  }

  private static void invalid(WireMessage<FixedPayload> wire) {
    var failure =
        assertThrows(PermanentProtocolException.class, () -> QuestionSubmitRequest.decode(wire));
    assertEquals("question submit request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static byte[] hash(QuestionSubmitRequest request, AuthenticatedActor actor) {
    try (var canonical = request.canonical(actor);
        var keys = new FingerprintKeyRing("test", new byte[32], null, null)) {
      return keys.calculate(canonical).digest();
    }
  }

  private static void check(QuestionSubmitRequest request, AuthenticatedActor actor, String body)
      throws Exception {
    try (var canonical = request.canonical(actor)) {
      assertEquals(Long.toString(actor.userId()), canonical.ownerScope());
      assertEquals("QSBREQ01", canonical.layoutId());
      assertEquals("001", canonical.layoutVersion());
      assertEquals("QUESTION:NEW", canonical.target());
      assertEquals(1, canonical.fields().size());
      var field = canonical.fields().getFirst();
      assertEquals("question", field.name());
      assertEquals("X1", field.typeVersion());
      assertArrayEquals(body.getBytes(StandardCharsets.UTF_8), field.value());
    }
    var bytes = new ByteArrayOutputStream();
    try (var output = new DataOutputStream(bytes)) {
      output.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      for (String value : List.of(Long.toString(actor.userId()), "QSBREQ01", "001", "QUESTION:NEW"))
        lp(output, value);
      output.writeInt(1);
      lp(output, "question");
      lp(output, "X1");
      lp(output, body);
    }
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
    assertArrayEquals(mac.doFinal(bytes.toByteArray()), hash(request, actor));
  }

  private static void lp(DataOutputStream output, String value) throws Exception {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    output.writeInt(bytes.length);
    output.write(bytes);
  }
}
