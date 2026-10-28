package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HexFormat;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** NK-PRO-002/UI232/SS322 §4,6,11; PT-CODEC-NFCGOLD001..003; independent scalar/hex goldens. */
class FieldCodecNfcGoldenTest {
  @Test
  void nfcGolden001HangulJamoFitsComposedByteWidth() {
    String[][] vectors = {
      {"\u1100\u1161", "\uac00", "eab080", "eab0802020", "e18480e185a1"},
      {"\u1100\u1161\u11a8", "\uac01", "eab081", "eab0812020", "e18480e185a1e186a8"}
    };
    for (String[] vector : vectors) {
      assertArrayEquals(hex(vector[2]), FieldCodec.encodeText(vector[0], 3, true));
      assertArrayEquals(hex(vector[3]), FieldCodec.encodeText(vector[0], 5, true));
      assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText(vector[0], 2, true));
      assertEquals(Optional.of(vector[1]), FieldCodec.decodeText(hex(vector[3]), true));
      byte[] noncanonical = hex(vector[4]);
      byte[] original = noncanonical.clone();
      assertThrows(
          PermanentProtocolException.class, () -> FieldCodec.decodeText(noncanonical, true));
      assertArrayEquals(original, noncanonical);
    }
  }

  @Test
  void nfcGolden002AngstromUsesCanonicalTwoByteScalarBeforeWidthCheck() {
    assertArrayEquals(hex("c385"), FieldCodec.encodeText("\u212b", 2, true));
    assertArrayEquals(hex("c38520"), FieldCodec.encodeText("\u212b", 3, false));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText("\u212b", 1, true));
    assertEquals(Optional.of("\u00c5"), FieldCodec.decodeText(hex("c38520"), false));
    byte[] noncanonical = hex("e284ab");
    assertThrows(PermanentProtocolException.class, () -> FieldCodec.decodeText(noncanonical, true));
    assertArrayEquals(hex("e284ab"), noncanonical);
  }

  @Test
  void nfcGolden003CanonicalCombiningOrderIsRequiredWithoutComposition() {
    String input = "q\u0301\u0323";
    assertArrayEquals(hex("71cca3cc81"), FieldCodec.encodeText(input, 5, true));
    assertArrayEquals(hex("71cca3cc8120"), FieldCodec.encodeText(input, 6, true));
    assertThrows(FieldEncodingException.class, () -> FieldCodec.encodeText(input, 4, true));
    assertEquals(Optional.of("q\u0323\u0301"), FieldCodec.decodeText(hex("71cca3cc8120"), true));
    byte[] noncanonical = hex("71cc81cca3");
    assertThrows(PermanentProtocolException.class, () -> FieldCodec.decodeText(noncanonical, true));
    assertArrayEquals(hex("71cc81cca3"), noncanonical);
  }

  private static byte[] hex(String value) {
    return HexFormat.of().parseHex(value);
  }
}
