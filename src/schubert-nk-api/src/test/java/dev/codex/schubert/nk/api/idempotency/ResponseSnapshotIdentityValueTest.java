package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.OptionalLong;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-IDEM-AADVALUE001..003; DAT009/UI241242/SS3246/35211.2; bytes only, no encryption/key. */
final class ResponseSnapshotIdentityValueTest {
  private static final UUID ID = UUID.fromString("00112233-4455-6677-8899-aabbccddeeff");
  private static final String LAYOUT = "QSSRSP01";
  private static final String VERSION = "001";
  // Generated independently by Python struct.pack LP8 from SS field widths, no production method.
  private static final String[] GOLDEN_HEX = {
    "000000126170692d696e626f782d726573706f6e73650000001673636875626572742e726571756573745f696e626f780000001000112233445566778899aabbccddeeff00000001010000000276310000000851535352535030310000000330303100000000",
    "000000126170692d696e626f782d726573706f6e73650000001673636875626572742e726571756573745f696e626f780000001000112233445566778899aabbccddeeff000000010100000002763100000008515353525350303100000003303031000000080000000000000001",
    "000000126170692d696e626f782d726573706f6e73650000001673636875626572742e726571756573745f696e626f780000001000112233445566778899aabbccddeeff00000001010000000276310000000851535352535030310000000330303100000008000000e8d4a50fff"
  };

  @Test
  void aadValue001RequiredComponentsLexicalAndOwnerBoundaries() {
    assertEquals(
        "requestMessageId",
        assertThrows(
                NullPointerException.class,
                () -> ResponseSnapshotIdentity.anonymous(null, LAYOUT, VERSION))
            .getMessage());
    assertEquals(
        "responseLayoutId",
        assertThrows(
                NullPointerException.class,
                () -> ResponseSnapshotIdentity.anonymous(ID, null, VERSION))
            .getMessage());
    assertEquals(
        "responseVersion",
        assertThrows(
                NullPointerException.class,
                () -> ResponseSnapshotIdentity.anonymous(ID, LAYOUT, null))
            .getMessage());
    assertEquals(
        "ownerUserId",
        assertThrows(
                NullPointerException.class,
                () -> new ResponseSnapshotIdentity(ID, LAYOUT, VERSION, null))
            .getMessage());
    for (String invalid : List.of("", "ABCDEFG", "ABCDEFGHI", "qssrsp01", "QSSRSP0é", "QSSRSP0 ")) {
      assertEquals(
          "responseLayoutId is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> ResponseSnapshotIdentity.anonymous(ID, invalid, VERSION))
              .getMessage());
    }
    for (String invalid : List.of("", "00", "0000", "00A", "０01", "01 ")) {
      assertEquals(
          "responseVersion is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> ResponseSnapshotIdentity.anonymous(ID, LAYOUT, invalid))
              .getMessage());
    }
    for (long invalid : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      assertEquals(
          "ownerUserId is outside N12",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> ResponseSnapshotIdentity.authenticated(ID, LAYOUT, VERSION, invalid))
              .getMessage());
    }
    ResponseSnapshotIdentity anonymous = ResponseSnapshotIdentity.anonymous(ID, "00000000", "000");
    assertEquals("00000000", anonymous.responseLayoutId());
    assertEquals("000", anonymous.responseVersion());
    assertFalse(anonymous.ownerUserId().isPresent());
    for (long owner : new long[] {1, 999_999_999_999L}) {
      assertEquals(
          OptionalLong.of(owner),
          ResponseSnapshotIdentity.authenticated(ID, "ZZZZZZZZ", "999", owner).ownerUserId());
    }
  }

  @Test
  void aadValue002ExactIndependentWholeVectorsAndCallOwnedBuffers() {
    List<ResponseSnapshotIdentity> values =
        List.of(
            ResponseSnapshotIdentity.anonymous(ID, LAYOUT, VERSION),
            ResponseSnapshotIdentity.authenticated(ID, LAYOUT, VERSION, 1),
            ResponseSnapshotIdentity.authenticated(ID, LAYOUT, VERSION, 999_999_999_999L));
    int[] lengths = {102, 110, 110};
    for (int i = 0; i < values.size(); i++) {
      ResponseSnapshotIdentity value = values.get(i);
      byte[] expected = HexFormat.of().parseHex(GOLDEN_HEX[i]);
      byte[] first = value.aad((byte) 1, "v1");
      byte[] second = value.aad((byte) 1, "v1");
      assertEquals(lengths[i], first.length);
      assertArrayEquals(expected, first);
      assertArrayEquals(expected, second);
      assertNotSame(first, second);
      first[0] = 99;
      assertArrayEquals(expected, second);
      assertArrayEquals(expected, value.aad((byte) 1, "v1"));
      assertEquals(
          "keyVersion",
          assertThrows(NullPointerException.class, () -> value.aad((byte) 1, null)).getMessage());
    }
  }

  @Test
  void aadValue003AllOrderedRecordComponentsHashAndFixedRedaction() {
    ResponseSnapshotIdentity value = ResponseSnapshotIdentity.authenticated(ID, LAYOUT, VERSION, 1);
    ResponseSnapshotIdentity equal =
        new ResponseSnapshotIdentity(ID, LAYOUT, VERSION, OptionalLong.of(1));
    assertEquals(ID, value.requestMessageId());
    assertEquals(LAYOUT, value.responseLayoutId());
    assertEquals(VERSION, value.responseVersion());
    assertEquals(OptionalLong.of(1), value.ownerUserId());
    assertEquals(
        "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]", value.toString());
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    // Python independent signed32 polynomial over UUID/String/String/OptionalLong hashes.
    assertEquals(-1889273649, value.hashCode());
    assertEquals("value", Map.of(value, "value").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "other type");
    for (ResponseSnapshotIdentity other :
        List.of(
            ResponseSnapshotIdentity.authenticated(new UUID(0, 2), LAYOUT, VERSION, 1),
            ResponseSnapshotIdentity.authenticated(ID, "QSDRSP01", VERSION, 1),
            ResponseSnapshotIdentity.authenticated(ID, LAYOUT, "002", 1),
            ResponseSnapshotIdentity.authenticated(ID, LAYOUT, VERSION, 2),
            ResponseSnapshotIdentity.anonymous(ID, LAYOUT, VERSION))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
