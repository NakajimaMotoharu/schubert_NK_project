package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.field;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
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
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/** UI232/235 byte offsets and independent SS352 JCE/AAD oracle. No expected production codec. */
final class MediaReplayFixture {
  private static final String FIXTURE_AUDIO_PREFIX = "AUD";
  private static final String FIXTURE_ANIMATION_PREFIX = "ANL";
  private static final String FIXTURE_VIDEO_PREFIX = "VID";
  private static final String FIXTURE_CATEGORY_PREFIX = "MCT";
  private static final String FIXTURE_SECTION_PREFIX = "MCS";
  private static final String FIXTURE_TRACK_PREFIX = "MTR";
  private static final String FIXTURE_MUSIC_PREFIX = "MED";
  private static final String FIXTURE_KEY_VERSION = "fixture";

  static final List<String> LAYOUTS =
      List.of(
          FIXTURE_AUDIO_PREFIX,
          "ANM",
          FIXTURE_ANIMATION_PREFIX,
          FIXTURE_VIDEO_PREFIX,
          FIXTURE_CATEGORY_PREFIX,
          FIXTURE_SECTION_PREFIX,
          FIXTURE_TRACK_PREFIX,
          FIXTURE_MUSIC_PREFIX);
  static final UUID RESPONSE = UUID.fromString("00000000-0000-4000-8000-000000000001");
  static final UUID NEXT = UUID.fromString("00000000-0000-4000-8000-000000000002");
  static final Instant COMPLETED = Instant.parse("2026-09-08T00:00:01.123456789Z");
  static final Instant SENT = Instant.parse("2026-09-08T00:00:02.789123456Z");
  static final String SHA = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";

  private MediaReplayFixture() {}

  static MediaRequest request(String prefix, String mode) {
    byte[] data = data(prefix + "REQ01");
    if (prefix.equals(FIXTURE_AUDIO_PREFIX)) put(data, 12, mode);
    if (prefix.equals(FIXTURE_MUSIC_PREFIX)) put(data, 64, mode);
    return MediaRequest.decode(message(prefix + "REQ01", data));
  }

  static MediaRequest rebound(MediaRequest request, byte[] data, String context) {
    var h = request.header();
    return MediaRequest.decode(
        new WireMessage<>(
            new CommonHeader(
                "SCHBNK01",
                1,
                h.layoutId(),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                h.messageId(),
                h.correlationId(),
                h.sentAt(),
                Optional.of(AuthenticationContext.of(context)),
                256,
                data.length,
                0,
                0,
                256 + data.length,
                Optional.empty()),
            new FixedPayload(data, 0, List.of())));
  }

  static int maximum(String prefix) {
    return switch (prefix) {
      case FIXTURE_ANIMATION_PREFIX -> 50;
      case FIXTURE_CATEGORY_PREFIX -> 20;
      case FIXTURE_SECTION_PREFIX -> 100;
      case FIXTURE_TRACK_PREFIX -> 200;
      default -> 0;
    };
  }

  static int recordLength(String prefix) {
    return switch (prefix) {
      case FIXTURE_ANIMATION_PREFIX -> 928;
      case FIXTURE_CATEGORY_PREFIX -> 72;
      case FIXTURE_SECTION_PREFIX -> 136;
      case FIXTURE_TRACK_PREFIX -> 1312;
      default -> 0;
    };
  }

  static byte[] responseData(
      String prefix, int count, String extension, String mode, boolean error) {
    byte[] result =
        field(
            switch (prefix) {
              case FIXTURE_AUDIO_PREFIX, FIXTURE_MUSIC_PREFIX -> 1024;
              case FIXTURE_VIDEO_PREFIX -> 1808;
              case "ANM", FIXTURE_TRACK_PREFIX -> 16;
              default -> 8;
            },
            0,
            "");
    if (List.of(FIXTURE_AUDIO_PREFIX, FIXTURE_VIDEO_PREFIX, FIXTURE_MUSIC_PREFIX)
        .contains(prefix)) {
      put(result, 832, "000000000000");
      if (!error) {
        String root =
            prefix.equals(FIXTURE_AUDIO_PREFIX)
                ? "scenario/"
                : prefix.equals(FIXTURE_VIDEO_PREFIX) ? "video/" : "music/";
        String id =
            prefix.equals(FIXTURE_AUDIO_PREFIX)
                ? "700"
                : prefix.equals(FIXTURE_VIDEO_PREFIX) ? "opening" : "music-0";
        put(result, 0, id);
        put(result, 64, root + "合成." + extension);
        put(result, 576, "表示." + extension);
        put(result, 832, "000000000003");
        put(result, 844, SHA);
        put(
            result,
            908,
            switch (extension) {
              case "mp4" -> "video/mp4";
              case "m4a" -> "audio/mp4";
              case "mp3" -> "audio/mpeg";
              case "ogg" -> "audio/ogg";
              case "wav" -> "audio/wav";
              case "flac" -> "audio/flac";
              default -> throw new AssertionError(extension);
            });
        put(result, 972, mode);
        if (prefix.equals(FIXTURE_VIDEO_PREFIX)) {
          put(result, 1024, "動画");
          put(result, 1280, "OPENING");
          put(result, 1296, "表示/動画.mp4");
        }
      }
      // BUG-043: UI232 §5.1 gives B=space on error; the opening byte is not an N field.
    } else if (prefix.equals("ANM")) put(result, 0, error ? "000000 000" : "0150041020");
    else number(result, 0, prefix.equals(FIXTURE_TRACK_PREFIX) ? 9 : 6, error ? 0 : count);
    return result;
  }

  static List<byte[]> records(String prefix, int count) {
    List<byte[]> records = new ArrayList<>();
    for (int i = 0; i < count; i++) {
      byte[] r = field(recordLength(prefix), 0, "");
      switch (prefix) {
        case FIXTURE_ANIMATION_PREFIX -> {
          put(r, 0, "video-" + i);
          put(r, 64, "動画" + i);
          put(r, 320, "MAIN");
          put(r, 336, "表示/a.mp4");
          number(r, 848, 12, 3);
          number(r, 924, 4, i);
        }
        case FIXTURE_CATEGORY_PREFIX -> {
          put(r, 0, "分類" + i);
          number(r, 64, 6, i + 1);
        }
        case FIXTURE_SECTION_PREFIX -> {
          put(r, 0, "区分" + i);
          number(r, 128, 6, i + 1);
        }
        case FIXTURE_TRACK_PREFIX -> {
          put(r, 0, "track-" + i);
          put(r, 64, "曲" + i);
          put(r, 320, "BGM");
          put(r, 384, "ゲーム");
          put(r, 512, "表示/a.ogg");
          number(r, 1024, 12, 3);
          put(r, 1292, "N");
          number(r, 1293, 4, i);
        }
        default -> throw new AssertionError(prefix);
      }
      records.add(r);
    }
    return records;
  }

  /** Production decoder makes test input objects only. All expected bytes remain hand-assembled. */
  static TypedPayloadValues typed(String prefix, int count, String extension, String mode) {
    return PayloadTypeCatalog.decode(
        PayloadCodec.standard()
            .decode(
                new LayoutId(prefix + "RSP01"),
                responseData(prefix, count, extension, mode, false),
                records(prefix, count),
                false));
  }

  static byte[] wire(
      String prefix,
      UUID correlation,
      UUID response,
      String timestamp,
      String context,
      String code,
      int count,
      String extension,
      String mode) {
    boolean error = !code.equals("0000") && !code.equals("0200");
    byte[] data = responseData(prefix, count, extension, mode, error);
    List<byte[]> records = records(prefix, error ? 0 : count);
    byte[] body = field(256 + data.length + records.size() * recordLength(prefix), 0, "");
    put(body, 0, "SCHBNK01001" + prefix + "RSP01001SS");
    put(body, 24, response.toString());
    put(body, 60, correlation.toString());
    put(body, 96, timestamp);
    put(body, 113, context);
    number(body, 177, 4, 256);
    number(body, 181, 6, data.length);
    number(body, 187, 6, recordLength(prefix));
    number(body, 193, 6, records.size());
    number(body, 199, 9, body.length);
    put(body, 208, code);
    System.arraycopy(data, 0, body, 256, data.length);
    int offset = 256 + data.length;
    for (byte[] r : records) {
      System.arraycopy(r, 0, body, offset, r.length);
      offset += r.length;
    }
    return body;
  }

  static void number(byte[] target, int offset, int width, long value) {
    put(target, offset, String.format(Locale.ROOT, "%0" + width + "d", value));
  }

  static byte[] key() {
    byte[] key = new byte[32];
    Arrays.fill(key, (byte) 3);
    return key;
  }

  static ResponseSnapshotCodec codec() {
    return new ResponseSnapshotCodec(FIXTURE_KEY_VERSION, key(), null, null);
  }

  static EncryptedResponseSnapshot encrypt(MediaRequest request, byte[] body) throws Exception {
    byte[] nonce = new byte[12];
    Arrays.fill(nonce, (byte) 7);
    var compressed = new ByteArrayOutputStream();
    var deflater = new Deflater(3);
    try (var stream = new DeflaterOutputStream(compressed, deflater)) {
      stream.write(body);
    } finally {
      deflater.end();
    }
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key(), "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad(request));
    var result = new ByteArrayOutputStream();
    result.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
    result.write(1);
    result.write(7);
    result.write(FIXTURE_KEY_VERSION.getBytes(StandardCharsets.US_ASCII));
    result.write(nonce);
    result.write(cipher.doFinal(compressed.toByteArray()));
    return new EncryptedResponseSnapshot(FIXTURE_KEY_VERSION, result.toByteArray());
  }

  static byte[] decrypt(MediaRequest request, EncryptedResponseSnapshot snapshot) throws Exception {
    ByteBuffer buffer = ByteBuffer.wrap(snapshot.ciphertext());
    byte[] magic = new byte[6];
    buffer.get(magic);
    assertArrayEquals("NKENC1".getBytes(StandardCharsets.US_ASCII), magic);
    assertEquals(1, buffer.get());
    assertEquals(7, buffer.get());
    byte[] version = new byte[7];
    buffer.get(version);
    assertArrayEquals(FIXTURE_KEY_VERSION.getBytes(StandardCharsets.US_ASCII), version);
    byte[] nonce = new byte[12];
    buffer.get(nonce);
    byte[] ciphertext = new byte[buffer.remaining()];
    buffer.get(ciphertext);
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE, new SecretKeySpec(key(), "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad(request));
    try (var stream =
        new InflaterInputStream(new ByteArrayInputStream(cipher.doFinal(ciphertext)))) {
      return stream.readAllBytes();
    }
  }

  private static byte[] aad(MediaRequest request) throws IOException {
    var bytes = new ByteArrayOutputStream();
    UUID id = request.header().messageId();
    try (var out = new DataOutputStream(bytes)) {
      for (byte[] field :
          List.of(
              "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
              "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(16)
                  .putLong(id.getMostSignificantBits())
                  .putLong(id.getLeastSignificantBits())
                  .array(),
              new byte[] {1},
              FIXTURE_KEY_VERSION.getBytes(StandardCharsets.US_ASCII),
              request
                  .header()
                  .layoutId()
                  .value()
                  .replace("REQ", "RSP")
                  .getBytes(StandardCharsets.US_ASCII),
              "001".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(8).putLong(101).array())) {
        out.writeInt(field.length);
        out.write(field);
      }
    }
    return bytes.toByteArray();
  }

  static InboxCompletion completion(MediaRequest request, byte[] body, InboxCompletionState state)
      throws Exception {
    return new InboxCompletion(
        state,
        InboxResultReference.none(),
        request.responseLayoutId().value(),
        "001",
        Optional.of(encrypt(request, body)),
        COMPLETED.truncatedTo(java.time.temporal.ChronoUnit.MICROS));
  }
}
