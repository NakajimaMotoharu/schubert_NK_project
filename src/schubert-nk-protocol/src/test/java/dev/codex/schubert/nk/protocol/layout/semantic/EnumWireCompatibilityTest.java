package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.ObjectStreamClass;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-PRO-001/SS323,333,354/BUG1474/YKT1237: private rename never changes enum wire contracts. */
final class EnumWireCompatibilityTest {
  /** PT-PRO-F03-ENUM001: Java serialization enum grammar, literal names and fixed descriptor. */
  @Test
  void enum001SerializedAnswerStateMatchesIndependentProtocolVector()
      throws IOException, ClassNotFoundException {
    var expected = new ByteArrayOutputStream();
    // STREAM_MAGIC/VERSION, TC_ENUM, TC_CLASSDESC, UTF length 58; not a production serializer.
    expected.writeBytes(HexFormat.of().parseHex("aced00057e72003a"));
    expected.writeBytes(
        "dev.codex.schubert.nk.protocol.layout.semantic.AnswerState"
            .getBytes(StandardCharsets.US_ASCII));
    // enum UID0/SC_ENUM|SC_SERIALIZABLE/fields0; java.lang.Enum descriptor; ANSWERED.
    expected.writeBytes(
        HexFormat.of()
            .parseHex(
                "00000000000000001200007872000e6a6176612e6c616e672e456e756d"
                    + "00000000000000001200007870740008414e535745524544"));
    var actual = new ByteArrayOutputStream();
    try (var stream = new ObjectOutputStream(actual)) {
      stream.writeObject(AnswerState.ANSWERED);
    }
    assertArrayEquals(expected.toByteArray(), actual.toByteArray());
    try (var stream = new ObjectInputStream(new ByteArrayInputStream(expected.toByteArray()))) {
      assertSame(AnswerState.ANSWERED, stream.readObject());
      assertEquals(-1, stream.read());
    }
  }

  /** PT-PRO-F03-ENUM002: all twenty-three protocol enum types have no serialized fields. */
  @Test
  void enum002EverySemanticEnumRetainsItsFieldIndependentSerialDescriptor() {
    for (Class<?> type :
        List.of(
            AnimationCategory.class,
            AnimationListCategory.class,
            AnswerState.class,
            ContentDisposition.class,
            DeliveryMode.class,
            EntryType.class,
            GameCode.class,
            LogLevel.class,
            LogType.class,
            MediaMimeType.class,
            NotificationErrorCode.class,
            NotificationState.class,
            NotificationType.class,
            PairRole.class,
            UserRole.class,
            UserState.class,
            VideoCategory.class,
            VoiceCondition.class,
            dev.codex.schubert.nk.protocol.header.InteractionKind.class,
            dev.codex.schubert.nk.protocol.header.MessageKind.class,
            dev.codex.schubert.nk.protocol.header.ResultCode.class,
            dev.codex.schubert.nk.protocol.file.ContentDisposition.class,
            dev.codex.schubert.nk.protocol.transport.BrokerTopology.class)) {
      var descriptor = ObjectStreamClass.lookup(type);
      assertEquals(0, descriptor.getFields().length, type.getName());
      assertEquals(0L, descriptor.getSerialVersionUID(), type.getName());
    }
  }
}
