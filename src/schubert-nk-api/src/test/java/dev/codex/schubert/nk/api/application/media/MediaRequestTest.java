package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.field;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.util.Arrays;
import java.util.List;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** Independent UI235 bytes and SS323 §9.2 LP/HMAC fields. PT-MED-033..035; SSC-029. */
class MediaRequestTest {
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(101, "reader", Role.USER);

  private record Field(String name, String type, String value) {}

  @Test
  void med033CanonicalFactoriesNormalizeOwnAndEraseBytes() {
    var text = CanonicalField.text("name", " e\u0301 ");
    try (text) {
      assertEquals("X1", text.typeVersion());
      assertEquals("name", text.name());
      byte[] expected = {32, (byte) 0xc3, (byte) 0xa9, 32};
      assertArrayEquals(expected, text.value());
      byte[] copy = text.value();
      Arrays.fill(copy, (byte) 0);
      assertArrayEquals(expected, text.value());
    }
    assertArrayEquals(new byte[4], text.value());
    for (String[] pair :
        List.of(
            new String[] {"-9223372036854775808"},
            new String[] {"0"},
            new String[] {"9223372036854775807"})) {
      var number = CanonicalField.number("id", Long.parseLong(pair[0]));
      try (number) {
        assertEquals("N1", number.typeVersion());
        assertArrayEquals(pair[0].getBytes(StandardCharsets.US_ASCII), number.value());
      }
      assertArrayEquals(new byte[pair[0].length()], number.value());
    }
    assertThrows(NullPointerException.class, () -> CanonicalField.text("name", null));
    assertThrows(NullPointerException.class, () -> CanonicalField.text(null, "value"));
    assertThrows(NullPointerException.class, () -> CanonicalField.number(null, 1));
    assertThrows(
        IllegalArgumentException.class, () -> CanonicalField.text("invalid name", "value"));
    assertThrows(IllegalArgumentException.class, () -> CanonicalField.number("", 1));
  }

  @Test
  void med034EightLayoutsHaveIndependentCanonicalFingerprints() throws Exception {
    check("ANMREQ01", data("ANMREQ01"), List.of());
    check("MCTREQ01", data("MCTREQ01"), List.of());
    for (String number : List.of("000000000001", "000000000700", "999999999999")) {
      for (String disposition : List.of("I", "A"))
        check(
            "AUDREQ01",
            field(16, 0, number + disposition),
            List.of(
                new Field("audioId", "N1", Long.toString(Long.parseLong(number))),
                new Field("disposition", "X1", disposition)));
    }
    for (String category : List.of("MAIN", "OVA"))
      check("ANLREQ01", field(16, 0, category), List.of(new Field("category", "X1", category)));
    for (String id : List.of("opening", "  é", "v".repeat(64))) {
      check("VIDREQ01", field(64, 0, id), List.of(new Field("videoId", "X1", id)));
      for (String disposition : List.of("I", "A")) {
        byte[] music = field(72, 0, id);
        put(music, 64, disposition);
        check(
            "MEDREQ01",
            music,
            List.of(new Field("trackId", "X1", id), new Field("disposition", "X1", disposition)));
      }
    }
    for (String category : List.of("曲", "BGM", "  é", "x".repeat(64))) {
      check("MCSREQ01", field(64, 0, category), List.of(new Field("category", "X1", category)));
      for (String section : List.of("ゲーム", "アニメ", "s".repeat(128))) {
        byte[] tracks = field(192, 0, category);
        put(tracks, 64, section);
        check(
            "MTRREQ01",
            tracks,
            List.of(new Field("category", "X1", category), new Field("section", "X1", section)));
      }
    }
  }

  @Test
  void med035MalformedNullAndUnknownRequestsNeverReachQueries() {
    assertThrows(NullPointerException.class, () -> MediaRequest.decode(null));
    for (String unknown : List.of("ZZZREQ01", "GAMREQ01", "AUDRSP01"))
      invalid(unknown, new byte[0]);
    for (String layout :
        List.of(
            "AUDREQ01",
            "ANMREQ01",
            "ANLREQ01",
            "VIDREQ01",
            "MCTREQ01",
            "MCSREQ01",
            "MTRREQ01",
            "MEDREQ01")) {
      byte[] source = data(layout);
      invalid(layout, Arrays.copyOf(source, source.length + 1));
      if (source.length > 0) {
        invalid(layout, Arrays.copyOf(source, source.length - 1));
        invalid(layout, field(source.length, 0, ""));
        source[0] = (byte) 0xc3;
        invalid(layout, source);
      }
    }
    invalid("ANLREQ01", field(16, 0, "SUBTRACK"));
    invalid("AUDREQ01", field(16, 0, "000000000000I"));
    invalid("AUDREQ01", field(16, 0, "000000000001Z"));
    invalid("VIDREQ01", field(64, 0, "e\u0301"));
    byte[] reserved = data("MEDREQ01");
    reserved[71] = 'X';
    invalid("MEDREQ01", reserved);
    var request = MediaRequest.decode(message("ANMREQ01", new byte[0]));
    assertThrows(NullPointerException.class, () -> request.canonical(null));
    Connection never =
        (Connection)
            Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] {Connection.class},
                (p, m, a) -> {
                  throw new AssertionError("null boundary touched JDBC");
                });
    assertThrows(NullPointerException.class, () -> request.query(null, never, ACTOR));
    assertThrows(
        NullPointerException.class, () -> request.query(new MediaRepository(), null, ACTOR));
    assertThrows(
        NullPointerException.class, () -> request.query(new MediaRepository(), never, null));
  }

  private static void invalid(String layout, byte[] data) {
    var failure =
        assertThrows(
            PermanentProtocolException.class, () -> MediaRequest.decode(message(layout, data)));
    assertEquals("media request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void check(String layout, byte[] data, List<Field> fields) throws Exception {
    var wire = message(layout, data);
    var request = MediaRequest.decode(wire);
    Arrays.fill(data, (byte) 0);
    assertSame(wire.header(), request.header());
    assertEquals(layout.replace("REQ", "RSP"), request.responseLayoutId().value());
    assertEquals("MediaRequest[REDACTED]", request.toString());
    byte[] key = new byte[32];
    Arrays.fill(key, (byte) 11);
    try (var keys = new FingerprintKeyRing("fixture", key, null, null)) {
      var canonical = request.canonical(ACTOR);
      try (canonical) {
        assertEquals("101", canonical.ownerScope());
        assertEquals(layout, canonical.layoutId());
        assertEquals("001", canonical.layoutVersion());
        assertEquals("REQUEST:" + layout, canonical.target());
        assertEquals(fields.size(), canonical.fields().size());
        var bytes = new ByteArrayOutputStream();
        try (var out = new DataOutputStream(bytes)) {
          out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
          for (String value : List.of("101", layout, "001", "REQUEST:" + layout)) lp(out, value);
          out.writeInt(fields.size());
          for (int i = 0; i < fields.size(); i++) {
            Field expected = fields.get(i);
            var actual = canonical.fields().get(i);
            assertEquals(expected.name(), actual.name());
            assertEquals(expected.type(), actual.typeVersion());
            assertArrayEquals(expected.value().getBytes(StandardCharsets.UTF_8), actual.value());
            lp(out, expected.name());
            lp(out, expected.type());
            lp(out, expected.value());
          }
        }
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(key, "HmacSHA256"));
        assertArrayEquals(mac.doFinal(bytes.toByteArray()), keys.calculate(canonical).digest());
      }
      for (var field : canonical.fields())
        assertArrayEquals(new byte[field.value().length], field.value());
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  private static void lp(DataOutputStream out, String value) throws Exception {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }
}
