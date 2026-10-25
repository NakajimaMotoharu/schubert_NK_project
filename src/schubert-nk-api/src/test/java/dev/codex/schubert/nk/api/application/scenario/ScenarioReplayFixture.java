package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.message;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.search;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.spaces;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
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

/** PT-SCN-009-S01..S05: UI232/234 offsets and SS352 LP/AES oracle, no production codec. */
final class ScenarioReplayFixture {
  static final UUID FILE = UUID.fromString("00000000-0000-4000-8000-000000000123");
  static final String PATH = "20260908/00000000-0000-4000-8000-000000000123.ready";
  static final String HASH = "a".repeat(64);
  static final List<String> LAYOUTS = List.of("GAM", "SPK", "RTE", "SCF", "SRC", "SCN");

  private ScenarioReplayFixture() {}

  static byte[] key() {
    byte[] key = new byte[32];
    Arrays.fill(key, (byte) 3);
    return key;
  }

  static ScenarioRequest request(String prefix) {
    byte[] data =
        switch (prefix) {
          case "GAM" -> new byte[0];
          case "SPK", "RTE" -> spaces(12);
          case "SCF" -> spaces(14);
          case "SRC" -> search();
          case "SCN" -> "000000000030".getBytes(StandardCharsets.US_ASCII);
          default -> throw new AssertionError(prefix);
        };
    if (List.of("SPK", "RTE", "SCF").contains(prefix)) put(data, 0, "NUKITASHI1");
    if (prefix.equals("SCF")) put(data, 12, "01");
    return ScenarioRequest.decode(message(prefix + "REQ01", data));
  }

  static ScenarioRequest newContext(ScenarioRequest request) {
    var h = request.header();
    byte[] data =
        switch (h.layoutId().value()) {
          case "GAMREQ01" -> new byte[0];
          case "SCNREQ01" -> "000000000030".getBytes(StandardCharsets.US_ASCII);
          default -> throw new AssertionError("context fixture is GAM/SCN only");
        };
    return ScenarioRequest.decode(
        new WireMessage<>(
            new CommonHeader(
                "SCHBNK01",
                1,
                h.layoutId(),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                h.messageId(),
                h.messageId(),
                h.sentAt(),
                Optional.of(AuthenticationContext.of("d".repeat(64))),
                256,
                data.length,
                0,
                0,
                256 + data.length,
                Optional.empty()),
            new FixedPayload(data, 0, List.of())));
  }

  /** Typed input is built independently from the byte fixture below. */
  static TypedPayloadValues typed(String prefix, boolean file, int count) {
    PayloadData data =
        switch (prefix) {
          case "GAM" -> new GameListResponseData(0);
          case "SPK" -> new SpeakerListResponseData(0);
          case "RTE" -> new RouteListResponseData(0);
          case "SCF" -> new ScenarioFileListResponseData(GameCode.NUKITASHI_1, 1, "共通", 0);
          case "SRC" -> new PagedResponseData(1, 100, 0, 1, 0, 0);
          case "SCN" -> metadata(30, file, count, PATH);
          default -> throw new AssertionError(prefix);
        };
    List<PayloadRecord> records = new ArrayList<>();
    if (prefix.equals("SCN") && !file) {
      for (int i = 1; i <= count; i++)
        records.add(
            new ScenarioEntryRecord(
                new EntryId(i),
                i,
                1,
                EntryType.NARRATION,
                Optional.empty(),
                "本文",
                0,
                Optional.empty(),
                Optional.empty()));
    }
    return new TypedPayloadValues(new LayoutId(prefix + "RSP01"), data, records);
  }

  static ScenarioDetailResponseData metadata(long id, boolean file, int count, String path) {
    return new ScenarioDetailResponseData(
        new ScriptFileId(id),
        GameCode.NUKITASHI_1,
        "Chapter",
        DisplayPath.of("scenario/01.txt"),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        file ? DeliveryMode.FILE : DeliveryMode.INLINE,
        file ? Optional.of(FILE) : Optional.empty(),
        file ? Optional.of(RelativePath.of(path)) : Optional.empty(),
        file ? 4800L * count : 0,
        file ? Optional.of(Sha256Hex.of(HASH)) : Optional.empty(),
        file ? 4800 : 0,
        file ? count : 0);
  }

  static byte[] data(String prefix, boolean file, int count, boolean error) {
    byte[] b =
        spaces(
            switch (prefix) {
              case "GAM", "SPK", "RTE" -> 9;
              case "SCF" -> 88;
              case "SRC" -> 48;
              case "SCN" -> 1728;
              default -> throw new AssertionError(prefix);
            });
    switch (prefix) {
      case "GAM", "SPK", "RTE" -> number(b, 0, 9, 0);
      case "SCF" -> {
        number(b, 12, 2, error ? 0 : 1);
        number(b, 78, 9, 0);
        if (!error) {
          put(b, 0, "NUKITASHI1");
          put(b, 14, "共通");
        }
      }
      case "SRC" -> {
        number(b, 0, 6, error ? 0 : 1);
        number(b, 6, 3, error ? 0 : 100);
        number(b, 9, 9, 0);
        number(b, 18, 6, error ? 0 : 1);
        number(b, 24, 9, 0);
        number(b, 33, 9, 0);
      }
      case "SCN" -> {
        number(b, 0, 12, error ? 0 : 30);
        number(b, 1621, 12, !error && file ? 4800L * count : 0);
        number(b, 1697, 6, !error && file ? 4800 : 0);
        number(b, 1703, 9, !error && file ? count : 0);
        if (!error) {
          put(b, 12, "NUKITASHI1");
          put(b, 24, "Chapter");
          put(b, 280, "scenario/01.txt");
          put(b, 1328, file ? "F" : "I");
          if (file) {
            put(b, 1329, FILE.toString());
            put(b, 1365, PATH);
            put(b, 1633, HASH);
          }
        }
      }
      default -> throw new AssertionError(prefix);
    }
    return b;
  }

  static byte[] wire(
      String prefix,
      UUID request,
      UUID response,
      String timestamp,
      String context,
      String code,
      boolean file,
      int count) {
    boolean error = !code.equals("0000") && !code.equals("0200");
    byte[] data = data(prefix, file, count, error);
    int length =
        switch (prefix) {
          case "GAM" -> 272;
          case "SPK" -> 152;
          case "RTE" -> 72;
          case "SCF" -> 800;
          case "SRC" -> 5584;
          case "SCN" -> 4800;
          default -> throw new AssertionError(prefix);
        };
    int records = prefix.equals("SCN") && !file && !error ? count : 0;
    byte[] body = spaces(256 + data.length + records * length);
    put(body, 0, "SCHBNK01001" + prefix + "RSP01001SS");
    put(body, 24, response.toString());
    put(body, 60, request.toString());
    put(body, 96, timestamp);
    put(body, 113, context);
    number(body, 177, 4, 256);
    number(body, 181, 6, data.length);
    number(body, 187, 6, length);
    number(body, 193, 6, records);
    number(body, 199, 9, body.length);
    put(body, 208, code);
    System.arraycopy(data, 0, body, 256, data.length);
    for (int i = 1; i <= records; i++) {
      int offset = 256 + data.length + (i - 1) * 4800;
      number(body, offset, 12, i);
      number(body, offset + 12, 6, i);
      number(body, offset + 18, 8, 1);
      put(body, offset + 26, "narration");
      put(body, offset + 164, "本文");
      number(body, offset + 4260, 3, 0);
    }
    return body;
  }

  static void number(byte[] target, int offset, int width, long value) {
    put(target, offset, String.format(Locale.ROOT, "%0" + width + "d", value));
  }

  /** Independent SS352 envelope; fixed nonce is a synthetic test key/vector only. */
  static EncryptedResponseSnapshot encrypt(ScenarioRequest request, byte[] body) throws Exception {
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
    cipher.updateAAD(aad(request, "fixture"));
    byte[] encrypted = cipher.doFinal(compressed.toByteArray());
    var envelope = new ByteArrayOutputStream();
    envelope.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
    envelope.write(1);
    envelope.write(7);
    envelope.write("fixture".getBytes(StandardCharsets.US_ASCII));
    envelope.write(nonce);
    envelope.write(encrypted);
    return new EncryptedResponseSnapshot("fixture", envelope.toByteArray());
  }

  static byte[] decrypt(ScenarioRequest request, EncryptedResponseSnapshot saved) throws Exception {
    ByteBuffer envelope = ByteBuffer.wrap(saved.ciphertext());
    byte[] magic = new byte[6];
    envelope.get(magic);
    org.junit.jupiter.api.Assertions.assertArrayEquals(
        "NKENC1".getBytes(StandardCharsets.US_ASCII), magic);
    org.junit.jupiter.api.Assertions.assertEquals(1, envelope.get());
    byte[] version = new byte[Byte.toUnsignedInt(envelope.get())];
    envelope.get(version);
    org.junit.jupiter.api.Assertions.assertEquals(
        "fixture", new String(version, StandardCharsets.US_ASCII));
    byte[] nonce = new byte[12];
    envelope.get(nonce);
    byte[] ciphertext = new byte[envelope.remaining()];
    envelope.get(ciphertext);
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE, new SecretKeySpec(key(), "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad(request, "fixture"));
    try (var stream =
        new InflaterInputStream(new ByteArrayInputStream(cipher.doFinal(ciphertext)))) {
      return stream.readAllBytes();
    }
  }

  private static byte[] aad(ScenarioRequest request, String keyVersion) throws IOException {
    var bytes = new ByteArrayOutputStream();
    try (var output = new DataOutputStream(bytes)) {
      var id = request.header().messageId();
      for (byte[] field :
          List.of(
              "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
              "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(16)
                  .putLong(id.getMostSignificantBits())
                  .putLong(id.getLeastSignificantBits())
                  .array(),
              new byte[] {1},
              keyVersion.getBytes(StandardCharsets.US_ASCII),
              (request.header().layoutId().value().substring(0, 3) + "RSP01")
                  .getBytes(StandardCharsets.US_ASCII),
              "001".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(8).putLong(101).array())) {
        output.writeInt(field.length);
        output.write(field);
      }
    }
    return bytes.toByteArray();
  }
}
