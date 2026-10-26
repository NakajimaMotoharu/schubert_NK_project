package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** PT-QRY009..012/NTF009; UI236 offsets and SS324 independent LP/HMAC, no expected codec. */
final class QuestionQueryRequestTest {
  private static final String QUESTION_QUERY_LAYOUT = "QSSREQ01";
  private static final String NOTIFICATION_QUERY_LAYOUT = "NTSREQ01";
  static final UUID MESSAGE = new UUID(100, 100);
  static final Instant NOW = Instant.parse("2026-10-01T00:00:01Z");
  static final AuthenticatedActor USER = new AuthenticatedActor(1, "u1", Role.USER);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);

  @Test
  void qry009CanonicalFieldsNullAndAllLayoutsUseIndependentJce() throws Exception {
    for (String layout :
        List.of(QUESTION_QUERY_LAYOUT, NOTIFICATION_QUERY_LAYOUT, "QSDREQ01", "NTDREQ01")) {
      for (boolean populated : List.of(false, true)) {
        var wire = message(layout, data(layout, populated));
        var request = QuestionQueryRequest.decode(wire);
        assertSame(wire.header(), request.header());
        assertEquals(layout.startsWith("QS"), request.questionScope());
        assertEquals(layout.contains("DREQ"), request.detailRequest());
        assertEquals(
            layout.equals(QUESTION_QUERY_LAYOUT) && populated, request.usernameSpecified());
        assertEquals(layout.substring(0, 3) + "RSP01", request.responseLayoutId().value());
        assertEquals("QuestionQueryRequest[REDACTED]", request.toString());
        List<String> names;
        List<String> types;
        List<String> values;
        if (layout.equals(QUESTION_QUERY_LAYOUT)) {
          names =
              List.of(
                  "keyword",
                  "username",
                  "answerState",
                  "submittedFrom",
                  "submittedTo",
                  "page",
                  "pageSize");
          types = List.of("X1", "X1", "X1", "T1", "T1", "N1", "N1");
          values =
              Arrays.asList(
                  populated ? "é_%\\" : null,
                  populated ? "u1" : null,
                  populated ? "ANSWERED" : null,
                  populated ? "2026-10-01T00:00:00.123Z" : null,
                  populated ? "2026-10-01T00:00:01.123Z" : null,
                  "999999",
                  "50");
        } else if (layout.equals(NOTIFICATION_QUERY_LAYOUT)) {
          names = List.of("notificationType", "submittedFrom", "submittedTo", "page", "pageSize");
          types = List.of("X1", "T1", "T1", "N1", "N1");
          values =
              Arrays.asList(
                  populated ? "COMPLETED" : null,
                  populated ? "2026-10-01T00:00:00.123Z" : null,
                  populated ? "2026-10-01T00:00:01.123Z" : null,
                  "999999",
                  "50");
        } else {
          names = List.of(layout.startsWith("QS") ? "questionId" : "notificationId");
          types = List.of("N1");
          values = List.of("999999999999");
        }
        try (var canonical = request.canonical(USER);
            var admin = request.canonical(ADMIN);
            var keys = new FingerprintKeyRing("test", new byte[32], null, null)) {
          assertEquals("1", canonical.ownerScope());
          assertEquals(layout, canonical.layoutId());
          assertEquals("001", canonical.layoutVersion());
          assertEquals("REQUEST:" + layout, canonical.target());
          var bytes = new ByteArrayOutputStream();
          try (var out = new DataOutputStream(bytes)) {
            out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
            for (String v : List.of("1", layout, "001", "REQUEST:" + layout)) lp(out, v);
            out.writeInt(names.size());
            for (int i = 0; i < names.size(); i++) {
              var field = canonical.fields().get(i);
              assertEquals(names.get(i), field.name());
              assertEquals(types.get(i), field.typeVersion());
              lp(out, names.get(i));
              lp(out, types.get(i));
              if (values.get(i) == null) {
                out.writeInt(-1);
                assertNull(field.value());
              } else {
                lp(out, values.get(i));
                assertArrayEquals(values.get(i).getBytes(StandardCharsets.UTF_8), field.value());
              }
            }
          }
          var mac = Mac.getInstance("HmacSHA256");
          mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
          assertArrayEquals(mac.doFinal(bytes.toByteArray()), keys.calculate(canonical).digest());
          assertArrayEquals(keys.calculate(canonical).digest(), keys.calculate(admin).digest());
        }
        byte[] before = wire.payload().copyData();
        request.canonical(USER).close();
        assertArrayEquals(before, wire.payload().copyData());
      }
    }
  }

  @Test
  void qry010MalformedNullAndRequestDependentPageAreRejected() {
    assertThrows(NullPointerException.class, () -> QuestionQueryRequest.decode(null));
    for (String layout :
        List.of(QUESTION_QUERY_LAYOUT, NOTIFICATION_QUERY_LAYOUT, "QSDREQ01", "NTDREQ01")) {
      var request = QuestionQueryRequest.decode(message(layout, data(layout, false)));
      assertThrows(NullPointerException.class, () -> request.canonical(null));
      assertThrows(NullPointerException.class, () -> request.validateResponse(null));
      assertThrows(NullPointerException.class, () -> request.query(null, null, null));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request.validateResponse(
                  new TypedPayloadValues(
                      new LayoutId("USRRSP01"),
                      new PagedResponseData(1, 50, 0, 1, 0, 0),
                      List.of())));
      byte[] bad = data(layout, false);
      bad[0] = 0;
      assertThrows(
          PermanentProtocolException.class,
          () -> QuestionQueryRequest.decode(message(layout, bad)));
      byte[] shortData = Arrays.copyOf(data(layout, false), data(layout, false).length - 1);
      assertThrows(
          PermanentProtocolException.class,
          () -> QuestionQueryRequest.decode(message(layout, shortData)));
    }
    assertThrows(
        PermanentProtocolException.class,
        () ->
            QuestionQueryRequest.decode(
                message("UDTREQ01", "000000000001".getBytes(StandardCharsets.US_ASCII))));
    for (String layout : List.of(QUESTION_QUERY_LAYOUT, NOTIFICATION_QUERY_LAYOUT)) {
      var request = QuestionQueryRequest.decode(message(layout, data(layout, false)));
      var response =
          new TypedPayloadValues(
              request.responseLayoutId(), new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
      request.validateResponse(response);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request.validateResponse(
                  new TypedPayloadValues(
                      request.responseLayoutId(),
                      new PagedResponseData(1, 50, 51, 2, 1, 50),
                      List.of())));
    }
  }

  static WireMessage<FixedPayload> message(String layout, byte[] data) {
    return new WireMessage<>(
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE,
            MESSAGE,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty()),
        new FixedPayload(data, 0, List.of()));
  }

  static byte[] data(String layout, boolean populated) {
    if (layout.contains("DREQ")) return "999999999999".getBytes(StandardCharsets.US_ASCII);
    byte[] b = new byte[layout.equals(QUESTION_QUERY_LAYOUT) ? 384 : 64];
    Arrays.fill(b, (byte) 32);
    if (layout.equals(QUESTION_QUERY_LAYOUT)) {
      if (populated) {
        put(b, 0, "é_%\\");
        put(b, 256, "u1");
        put(b, 320, "ANSWERED");
        put(b, 332, "20261001090000123");
        put(b, 349, "20261001090001123");
      }
      put(b, 366, "999999050");
    } else {
      if (populated) {
        put(b, 0, "COMPLETED");
        put(b, 12, "20261001090000123");
        put(b, 29, "20261001090001123");
      }
      put(b, 46, "999999050");
    }
    return b;
  }

  static void put(byte[] data, int offset, String value) {
    byte[] b = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(b, 0, data, offset, b.length);
  }

  static void lp(DataOutputStream out, String value) throws IOException {
    byte[] b = value.getBytes(StandardCharsets.UTF_8);
    out.writeInt(b.length);
    out.write(b);
  }
}
