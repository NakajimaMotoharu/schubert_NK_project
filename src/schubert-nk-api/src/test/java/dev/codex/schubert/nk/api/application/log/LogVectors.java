package dev.codex.schubert.nk.api.application.log;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import java.util.zip.InflaterInputStream;
import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/** Independent UI235 offsets and SS323/352 LP/JCE vectors; synthetic values only, PT061..066. */
final class LogVectors {
  static final Instant NOW = Instant.parse("2026-09-08T00:00:00Z");
  static final Instant COMPLETED = NOW.plusNanos(123456789);
  static final Instant LATER = NOW.plusSeconds(3600);
  static final UUID MESSAGE = new UUID(200, 1);
  static final UUID RESPONSE = new UUID(201, 1);
  static final UUID REPLY = new UUID(201, 2);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "admin", Role.ADMIN);
  static final String[] NAMES = {
    "keyword", "logType", "action", "path", "level", "fromAt", "toAt", "page", "pageSize"
  };

  static void put(byte[] bytes, int offset, String value) {
    byte[] text = Normalizer.normalize(value, Normalizer.Form.NFC).getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }

  static String time(Instant value) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(value);
  }

  static byte[] data(List<String> fields, int page) {
    byte[] bytes = new byte[656];
    Arrays.fill(bytes, (byte) 32);
    int[] offsets = {0, 256, 272, 336, 592, 600, 617};
    for (int i = 0; i < 7; i++)
      if (fields.get(i) != null)
        put(bytes, offsets[i], i >= 5 ? time(Instant.parse(fields.get(i))) : fields.get(i));
    put(bytes, 634, String.format(Locale.ROOT, "%06d100", page));
    return bytes;
  }

  static List<String> emptyFilters() {
    return Arrays.asList(null, null, null, null, null, null, null);
  }

  static WireMessage<FixedPayload> message(String layout, byte[] bytes, UUID id) {
    return new WireMessage<>(
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            bytes.length,
            0,
            0,
            256 + bytes.length,
            Optional.empty()),
        new FixedPayload(bytes, 0, List.of()));
  }

  static LogRequest request(List<String> fields, int page, UUID id) {
    return LogRequest.decode(message("LGSREQ01", data(fields, page), id));
  }

  static LogRequest request(int page) {
    return request(emptyFilters(), page, MESSAGE);
  }

  static void lp(DataOutputStream out, String value) throws IOException {
    if (value == null) {
      out.writeInt(-1);
      return;
    }
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  static byte[] check(LogRequest request, AuthenticatedActor actor, List<String> filters, int page)
      throws Exception {
    var expected = new ArrayList<>(filters);
    expected.add(Integer.toString(page));
    expected.add("100");
    var bytes = new ByteArrayOutputStream();
    try (var canonical = request.canonical(actor);
        var keys = new FingerprintKeyRing("test", new byte[32], null, null);
        var out = new DataOutputStream(bytes)) {
      assertEquals(Long.toString(actor.userId()), canonical.ownerScope());
      assertEquals("LGSREQ01", canonical.layoutId());
      assertEquals("001", canonical.layoutVersion());
      assertEquals("REQUEST:LGSREQ01", canonical.target());
      assertEquals(9, canonical.fields().size());
      out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      for (String v : List.of(Long.toString(actor.userId()), "LGSREQ01", "001", "REQUEST:LGSREQ01"))
        lp(out, v);
      out.writeInt(9);
      for (int i = 0; i < 9; i++) {
        String type = i >= 7 ? "N1" : i >= 5 ? "T1" : "X1";
        var field = canonical.fields().get(i);
        assertEquals(NAMES[i], field.name());
        assertEquals(type, field.typeVersion());
        lp(out, NAMES[i]);
        lp(out, type);
        lp(out, expected.get(i));
        if (expected.get(i) == null) assertNull(field.value());
        else assertArrayEquals(expected.get(i).getBytes(StandardCharsets.UTF_8), field.value());
      }
      var mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
      byte[] digest = mac.doFinal(bytes.toByteArray());
      assertArrayEquals(digest, keys.calculate(canonical).digest());
      return digest;
    }
  }

  static TypedPayloadValues page(int count, long total, int page, boolean optional) {
    List<PayloadRecord> rows = new ArrayList<>();
    for (int i = 1; i <= count; i++)
      rows.add(
          new LogRecord(
              new LogId(i),
              NOW,
              LogType.ACTION,
              LogLevel.INFO,
              optional ? Optional.of("TEST") : Optional.empty(),
              "message " + i,
              optional ? Optional.of(new UUID(0, 1)) : Optional.empty(),
              optional ? Optional.of(new UUID(0, 2)) : Optional.empty(),
              optional ? Optional.of(new UUID(0, 3)) : Optional.empty(),
              optional ? Optional.of("GET") : Optional.empty(),
              optional ? Optional.of("/safe") : Optional.empty(),
              optional ? Optional.of(new HttpStatusCode(200)) : Optional.empty(),
              optional ? Optional.of(new ElapsedMilliseconds(0)) : Optional.empty(),
              optional ? Optional.of("2001:db8::1") : Optional.empty(),
              optional ? Optional.of("{\"count\": 1}") : Optional.empty()));
    return new TypedPayloadValues(
        new LayoutId("LGSRSP01"),
        new PagedResponseData(
            page,
            100,
            total,
            Math.max(1, (int) ((total + 99) / 100)),
            total == 0 ? 0 : (page - 1L) * 100 + 1,
            Math.min(page * 100L, total)),
        rows);
  }

  static byte[] wire(
      UUID request,
      UUID response,
      Instant time,
      String code,
      int count,
      long total,
      int page,
      boolean optional) {
    boolean success = code.equals("0000") || code.equals("0200");
    int records = success ? count : 0;
    byte[] bytes = new byte[304 + 2088 * records];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, 0, "SCHBNK01001LGSRSP01001SS");
    put(bytes, 24, response.toString());
    put(bytes, 60, request.toString());
    put(bytes, 96, time(time));
    put(bytes, 113, "b".repeat(64));
    put(bytes, 177, String.format(Locale.ROOT, "0256000048002088%06d%09d", records, bytes.length));
    put(bytes, 208, code);
    if (success)
      put(
          bytes,
          256,
          String.format(
              Locale.ROOT,
              "%06d100%09d%06d%09d%09d",
              page,
              total,
              Math.max(1, (total + 99) / 100),
              total == 0 ? 0 : (page - 1L) * 100 + 1,
              Math.min(page * 100L, total)));
    else put(bytes, 256, "0".repeat(42));
    for (int i = 1; i <= records; i++) {
      int o = 304 + (i - 1) * 2088;
      put(bytes, o, String.format(Locale.ROOT, "%012d", i));
      put(bytes, o + 12, time(NOW));
      put(bytes, o + 29, "ACTION");
      put(bytes, o + 45, "INFO");
      put(bytes, o + 117, "message " + i);
      if (optional) {
        put(bytes, o + 53, "TEST");
        put(bytes, o + 629, new UUID(0, 1).toString());
        put(bytes, o + 665, new UUID(0, 2).toString());
        put(bytes, o + 701, new UUID(0, 3).toString());
        put(bytes, o + 737, "GET");
        put(bytes, o + 745, "/safe");
        put(bytes, o + 1001, "200");
        put(bytes, o + 1004, "0");
        put(bytes, o + 1013, "2001:db8::1");
        put(bytes, o + 1058, "{\"count\": 1}");
      }
    }
    return bytes;
  }

  private static byte[] aad(UUID source, long owner, String layout) throws Exception {
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      for (byte[] field :
          List.of(
              "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
              "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(16)
                  .putLong(source.getMostSignificantBits())
                  .putLong(source.getLeastSignificantBits())
                  .array(),
              new byte[] {1},
              "test".getBytes(StandardCharsets.US_ASCII),
              layout.getBytes(StandardCharsets.US_ASCII),
              "001".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(8).putLong(owner).array())) {
        out.writeInt(field.length);
        out.write(field);
      }
    }
    return bytes.toByteArray();
  }

  static EncryptedResponseSnapshot encrypt(byte[] plaintext, UUID source, long owner, String layout)
      throws Exception {
    var output = new ByteArrayOutputStream();
    var deflater = new Deflater(3);
    try (var stream = new DeflaterOutputStream(output, deflater)) {
      stream.write(plaintext);
    } finally {
      deflater.end();
    }
    // Fixed nonce and key only in independent synthetic test vectors.
    byte[] nonce = new byte[12];
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad(source, owner, layout));
    byte[] encrypted = cipher.doFinal(output.toByteArray());
    return new EncryptedResponseSnapshot(
        "test",
        ByteBuffer.allocate(24 + encrypted.length)
            .put("NKENC1".getBytes(StandardCharsets.US_ASCII))
            .put((byte) 1)
            .put((byte) 4)
            .put("test".getBytes(StandardCharsets.US_ASCII))
            .put(nonce)
            .put(encrypted)
            .array());
  }

  static byte[] decrypt(InboxCompletion completion, UUID source, long owner) throws Exception {
    byte[] bytes = completion.responseSnapshot().orElseThrow().ciphertext();
    assertArrayEquals(
        "NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(bytes, 0, 6));
    assertEquals(1, bytes[6]);
    assertEquals(4, bytes[7]);
    assertArrayEquals("test".getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(bytes, 8, 12));
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, Arrays.copyOfRange(bytes, 12, 24)));
    cipher.updateAAD(aad(source, owner, completion.responseLayoutId()));
    try (var inflater =
        new InflaterInputStream(
            new ByteArrayInputStream(
                cipher.doFinal(Arrays.copyOfRange(bytes, 24, bytes.length))))) {
      return inflater.readAllBytes();
    }
  }
}
