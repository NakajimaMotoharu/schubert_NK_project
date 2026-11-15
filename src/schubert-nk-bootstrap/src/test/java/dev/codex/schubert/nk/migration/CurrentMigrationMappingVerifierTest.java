package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MIG-MAPVERIFY001..016; Python golden and independently reframed malformed data, no IO. */
final class CurrentMigrationMappingVerifierTest {
  private static final String MAGIC = "NKMIGMAPPING1\n";
  private static final String PART_FILES = "FILES";
  private static final String PART_ENTRIES = "ENTRIES";
  private static final String PART_SPEAKERS = "SPEAKERS";
  private static final String PART_AUDIO = "AUDIO";
  private static final String MAX_INT_TEXT = "2147483647";
  private static final String DIAGNOSTIC = "migration mapping serialization is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> KINDS =
      List.of(PART_FILES, PART_ENTRIES, PART_SPEAKERS, PART_AUDIO);
  private static final Map<String, Integer> TWO =
      Map.of(PART_FILES, 2, PART_ENTRIES, 2, PART_SPEAKERS, 2, PART_AUDIO, 2);
  private static final String NORMAL =
      "NKMIGMAPPING1\nFILES\t2\t37\t9c5820c79b521c94a56a2b07bf070756a1e7fe84f64b090740e1338483ee867a\nNKMIGFILEORDER1\n1\t-5\t101\t1\n2\t5\t401\t1\nENTRIES\t2\t56\t412afc944908b31f37ee180a3c3043262ebed7643c2d240f8b23e683ca6657cf\nNKMIGENTRYPLACEMENT1\n-10\t201\t1\t1\t101\t0\n20\t901\t2\t2\t401\t0\nSPEAKERS\t2\t58\tf07376a3f3c4c9c13d3b20eab12b5626091eeee779babebb68d74d8e1fcf6dc6\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-3\t1\n2\t4\t6\nAUDIO\t2\t56\t80b919a39739429d9c905d3a1730aba0faa88a340155c2bb0a50889b41720cb3\ngame_id\tcurrent_audio_id\ttarget_audio_id\n1\t-5\t21\n2\t8\t32\n";
  private static final String NORMAL_HASH =
      "33a5b664c4abaa54e4f2d403e70a3f2545aa6395a06ebcc7196f404749985ca4";
  private static final String EMPTY =
      "NKMIGMAPPING1\nFILES\t0\t16\tfee61b49e4c39e9062c2c6e845fefe03ca5160ce7b8881791b8338085d7e473a\nNKMIGFILEORDER1\nENTRIES\t0\t21\t5946c60b76d7bd7a3efa92a5bcc5d773d9e558a3b6260baea98e9e104ede6f30\nNKMIGENTRYPLACEMENT1\nSPEAKERS\t0\t45\t6ba2aea78407a77e5467625c22e68382bd06a746d097af921057a0f89a3acc13\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\nAUDIO\t0\t41\t6a09be7493407eb5d1d18db65c2de8d7898eef78648b626ab8d0c81005cdede5\ngame_id\tcurrent_audio_id\ttarget_audio_id\n";
  private static final String EMPTY_HASH =
      "83b87552a2f59f743b0c28ad12ed8bbb5e0f38c4a3794c68a29f35a3974284e9";
  private static final String ONE_FILE =
      "NKMIGMAPPING1\nFILES\t1\t25\t4f704e2edf473a1a5c2cc3cb29a168f3acac78f61fc276ce87c9f9c5b1c8db6f\nNKMIGFILEORDER1\n1\t9\t90\t1\nENTRIES\t0\t21\t5946c60b76d7bd7a3efa92a5bcc5d773d9e558a3b6260baea98e9e104ede6f30\nNKMIGENTRYPLACEMENT1\nSPEAKERS\t0\t45\t6ba2aea78407a77e5467625c22e68382bd06a746d097af921057a0f89a3acc13\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\nAUDIO\t0\t41\t6a09be7493407eb5d1d18db65c2de8d7898eef78648b626ab8d0c81005cdede5\ngame_id\tcurrent_audio_id\ttarget_audio_id\n";
  private static final String ONE_FILE_HASH =
      "ac411723896848964fb14c8fac3945bc758ffa1bdc1ffc83ac9a872775df07f5";
  private static final String BOUNDARY =
      "NKMIGMAPPING1\nFILES\t2\t80\t88acd97c20f6df8d75afce084077141f0e712d07ecc23433e17c110ddba60aa9\nNKMIGFILEORDER1\n1\t-9223372036854775808\t1\t1\n2\t9223372036854775807\t999999999999\t1\nENTRIES\t2\t104\t9fd7e5409bb4fbe3b2f0fae72677416a00dfd435ab8b5af8497105fe4a745364\nNKMIGENTRYPLACEMENT1\n-9223372036854775808\t2\t1\t1\t1\t0\n9223372036854775807\t999999999998\t2\t2\t999999999999\t0\nSPEAKERS\t2\t105\tedb26e744dfe8422bf5e0227298e221f8ac22ca834ca4a84e9b25e1a48357c7f\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-9223372036854775808\t3\n2\t9223372036854775807\t999999999997\nAUDIO\t2\t101\tb57f5526485b2caa8e18a6d45578cfc2ad1214726ef1284a7935da83145ae37c\ngame_id\tcurrent_audio_id\ttarget_audio_id\n1\t-9223372036854775808\t4\n2\t9223372036854775807\t999999999996\n";
  private static final String BOUNDARY_HASH =
      "d2d9bfab039646d27abd0afb8694553fbd4df6eedfff93dd92e82e19acf8b0e5";
  private static final String OVERLAP =
      "NKMIGMAPPING1\nFILES\t2\t37\t9c5820c79b521c94a56a2b07bf070756a1e7fe84f64b090740e1338483ee867a\nNKMIGFILEORDER1\n1\t-5\t101\t1\n2\t5\t401\t1\nENTRIES\t2\t56\t412afc944908b31f37ee180a3c3043262ebed7643c2d240f8b23e683ca6657cf\nNKMIGENTRYPLACEMENT1\n-10\t201\t1\t1\t101\t0\n20\t901\t2\t2\t401\t0\nSPEAKERS\t2\t62\t934746dd24a1e6367a1dae234c329f84312825da86d8586743954cbcd277f96f\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-3\t101\n2\t4\t401\nAUDIO\t2\t58\t4e877fc321c01cb7c528dc76f55199881138951b6dd806fb2b13ef30ca3be6e3\ngame_id\tcurrent_audio_id\ttarget_audio_id\n1\t-5\t101\n2\t8\t401\n";
  private static final String OVERLAP_HASH =
      "1e856526747d19fa4761cccfc05dff7dc276e04dc2eb4a7ee5ef2cc1eacb0868";
  private static final List<String> PARTS =
      List.of(
          "NKMIGFILEORDER1\n1\t-5\t101\t1\n2\t5\t401\t1\n",
          "NKMIGENTRYPLACEMENT1\n-10\t201\t1\t1\t101\t0\n20\t901\t2\t2\t401\t0\n",
          "game_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-3\t1\n2\t4\t6\n",
          "game_id\tcurrent_audio_id\ttarget_audio_id\n1\t-5\t21\n2\t8\t32\n");

  @Test
  void mapverify001FiveIndependentGoldenArtifactsAndCounts() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    assertEquals(TWO, verifier.verify(bytes(NORMAL), NORMAL_HASH));
    assertEquals(TWO, verifier.verify(bytes(BOUNDARY), BOUNDARY_HASH));
    assertEquals(TWO, verifier.verify(bytes(OVERLAP), OVERLAP_HASH));
    assertEquals(
        Map.of(PART_FILES, 0, PART_ENTRIES, 0, PART_SPEAKERS, 0, PART_AUDIO, 0),
        verifier.verify(bytes(EMPTY), EMPTY_HASH));
    assertEquals(
        Map.of(PART_FILES, 1, PART_ENTRIES, 0, PART_SPEAKERS, 0, PART_AUDIO, 0),
        verifier.verify(bytes(ONE_FILE), ONE_FILE_HASH));
    assertArrayEquals(bytes(NORMAL), new Wire().encode());
  }

  @Test
  void mapverify002MissingAndMalformedExpectedHashNeverNormalize() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    reject(verifier, null, NORMAL_HASH);
    reject(verifier, bytes(NORMAL), null);
    for (String hash :
        List.of(
            "", "A".repeat(64), "0".repeat(63), "0".repeat(65), "g".repeat(64), " " + NORMAL_HASH))
      reject(verifier, bytes(NORMAL), hash);
  }

  @Test
  void mapverify003WholeDigestMismatchAndInputAreUnchanged() throws Exception {
    byte[] changed = bytes(NORMAL);
    changed[changed.length - 1] = 0;
    reject(new CurrentMigrationMappingVerifier(), changed, NORMAL_HASH);
    reject(new CurrentMigrationMappingVerifier(), bytes(NORMAL), "0".repeat(64));
    byte[] source = bytes(NORMAL);
    byte[] before = source.clone();
    assertEquals(TWO, new CurrentMigrationMappingVerifier().verify(source, NORMAL_HASH));
    assertArrayEquals(before, source);
  }

  @Test
  void mapverify004MagicAndEveryShortPrefixFailEvenWithMatchingDigest() throws Exception {
    for (int length = 0; length <= bytes(MAGIC).length; length++)
      reject(Arrays.copyOf(bytes(NORMAL), length));
    byte[] wrong = bytes(NORMAL);
    wrong[0] = 'X';
    reject(wrong);
  }

  @Test
  void mapverify005KindOrderUnknownDuplicateMissingAndTrailingBytes() throws Exception {
    for (int part = 0; part < KINDS.size(); part++)
      for (String kind : List.of("", "unknown", "files", KINDS.get((part + 1) % KINDS.size()))) {
        var wire = new Wire();
        wire.field(part, 0, kind);
        reject(wire.encode());
      }
    var extra = new Wire();
    extra.suffix = "X";
    reject(extra.encode());
    extra.suffix = "\n";
    reject(extra.encode());
    byte[] normal = bytes(NORMAL);
    reject(Arrays.copyOf(normal, normal.length - 1));
  }

  @Test
  void mapverify006HeaderArityAsciiControlLengthAndNewline() throws Exception {
    for (String header :
        List.of(
            PART_FILES,
            "FILES\t0",
            "FILES\t0\t1",
            new Wire().header(0) + "\tX",
            "X".repeat(96),
            "FILES\r",
            PART_FILES + (char) 0,
            PART_FILES + (char) 127,
            "FILÉS")) {
      var wire = new Wire();
      wire.overrides.put(0, header);
      reject(wire.encode());
    }
    reject(bytes(MAGIC + "FILES\t"));
    byte[] high = bytes(NORMAL);
    high[bytes(MAGIC).length] = (byte) 0x80;
    reject(high);
  }

  @Test
  void mapverify007CountAndLengthCanonicalDecimalAndOverflow() throws Exception {
    for (int field : List.of(1, 2))
      for (String value :
          List.of(
              "",
              "-1",
              "-0",
              "+1",
              "00",
              "01",
              "2147483648",
              "9223372036854775808",
              "-9223372036854775809",
              "99999999999999999999",
              "1.0",
              " 1",
              "1 ")) {
        var wire = new Wire();
        wire.field(0, field, value);
        reject(wire.encode());
      }
    var huge = new Wire();
    huge.field(2, 1, MAX_INT_TEXT);
    huge.field(2, 2, MAX_INT_TEXT);
    reject(huge.encode());
    huge = new Wire();
    huge.field(0, 1, MAX_INT_TEXT);
    reject(huge.encode());
  }

  @Test
  void mapverify008AllPartDigestFieldsAndPayloadBounds() throws Exception {
    for (int part = 0; part < KINDS.size(); part++) {
      for (String hash :
          List.of(
              "", "A".repeat(64), "0".repeat(63), "0".repeat(65), "g".repeat(64), "0".repeat(64))) {
        var wire = new Wire();
        wire.field(part, 3, hash);
        reject(wire.encode());
      }
      var shortBody = new Wire();
      shortBody.field(part, 2, MAX_INT_TEXT);
      reject(shortBody.encode());
    }
  }

  @Test
  void mapverify009ChildHeadersRowsColumnsLineLimitsAndControl() throws Exception {
    for (int part = 0; part < KINDS.size(); part++) {
      String childHeader = PARTS.get(part).split("\n", -1)[0];
      for (String body :
          List.of(
              "",
              "\n",
              "wrong\n",
              PARTS.get(part).stripTrailing(),
              childHeader + "\n1\n",
              childHeader + "\n\n",
              childHeader + "\n" + "1".repeat(126) + "\n",
              childHeader + "\n1\té\t2\n",
              childHeader + "\n1\t" + (char) 0 + "\t2\n",
              childHeader + "\n1\t" + (char) 127 + "\t2\n",
              childHeader + "\n1\t2\r\t3\n")) {
        var wire = new Wire();
        wire.parts.set(part, body);
        wire.field(part, 1, "0");
        reject(wire.encode());
      }
      var wrongWidth = new Wire();
      wrongWidth.parts.set(part, childHeader + "\n1\n");
      wrongWidth.field(part, 1, "1");
      reject(wrongWidth.encode());
      var wrongCount = new Wire();
      wrongCount.field(part, 1, "1");
      reject(wrongCount.encode());
      var wrongHeader = new Wire();
      wrongHeader.parts.set(part, "X" + PARTS.get(part));
      reject(wrongHeader.encode());
    }
  }

  @Test
  void mapverify010SignedLongLexicalAndUnsignedBounds() throws Exception {
    for (String value :
        List.of(
            "",
            "-0",
            "+1",
            "00",
            "01",
            " 1",
            "1 ",
            "1.0",
            "x",
            "9223372036854775808",
            "-9223372036854775809")) {
      var wire = new Wire();
      wire.cell(0, 0, 1, value);
      reject(wire.encode());
    }
    for (String value : List.of("-1", "2147483648")) {
      var wire = new Wire();
      wire.cell(1, 0, 5, value);
      reject(wire.encode());
    }
    var max = new Wire();
    max.cell(1, 0, 5, MAX_INT_TEXT);
    valid(max);
  }

  @Test
  void mapverify011FileGamePkTargetOrderAndDerivedDisplayAreCanonical() throws Exception {
    for (String game : List.of("0", "3")) {
      var wire = new Wire();
      wire.cell(0, 0, 0, game);
      reject(wire.encode());
    }
    for (String id : List.of("0", "1000000000000")) {
      var wire = new Wire();
      wire.cell(0, 0, 2, id);
      reject(wire.encode());
    }
    var duplicate = new Wire();
    duplicate.cell(0, 1, 2, "101");
    reject(duplicate.encode());
    duplicate = new Wire();
    duplicate.cell(0, 1, 0, "1");
    duplicate.cell(0, 1, 1, "-5");
    reject(duplicate.encode());
    var order = new Wire();
    order.reverse(0);
    reject(order.encode());
    order = new Wire();
    order.cell(0, 0, 3, "2");
    reject(order.encode());
    var qualifiedCurrent = new Wire();
    qualifiedCurrent.cell(0, 1, 1, "-5");
    valid(qualifiedCurrent);
  }

  @Test
  void mapverify012EntryFileGamePkOrderIndexAndIndependentTargets() throws Exception {
    var wire = new Wire();
    wire.cell(1, 0, 4, "999");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 0, 3, "2");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 1, 0, "-10");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 1, 1, "201");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 0, 2, "2");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 1, 3, "1");
    wire.cell(1, 1, 4, "101");
    reject(wire.encode());
    wire = new Wire();
    wire.reverse(1);
    reject(wire.encode());
    wire = new Wire();
    wire.cell(1, 0, 1, "901");
    wire.cell(1, 1, 1, "201");
    valid(wire);
  }

  @Test
  void mapverify013SpeakerPkGameTargetAndCurrentCanonicalOrder() throws Exception {
    for (String game : List.of("0", "3")) {
      var wire = new Wire();
      wire.cell(2, 0, 0, game);
      reject(wire.encode());
    }
    for (String id : List.of("0", "1000000000000")) {
      var wire = new Wire();
      wire.cell(2, 0, 2, id);
      reject(wire.encode());
    }
    var wire = new Wire();
    wire.cell(2, 1, 1, "-3");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(2, 1, 2, "1");
    reject(wire.encode());
    wire = new Wire();
    wire.reverse(2);
    reject(wire.encode());
    wire = new Wire();
    wire.cell(2, 0, 2, "6");
    wire.cell(2, 1, 2, "1");
    valid(wire);
  }

  @Test
  void mapverify014AudioGameN12AndStrictCurrentAndTargetOrder() throws Exception {
    for (String game : List.of("0", "3")) {
      var wire = new Wire();
      wire.cell(3, 0, 0, game);
      reject(wire.encode());
    }
    for (String id : List.of("0", "1000000000000")) {
      var wire = new Wire();
      wire.cell(3, 0, 2, id);
      reject(wire.encode());
    }
    var wire = new Wire();
    wire.cell(3, 1, 1, "-5");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(3, 1, 2, "21");
    reject(wire.encode());
    wire = new Wire();
    wire.cell(3, 1, 2, "20");
    reject(wire.encode());
    wire = new Wire();
    wire.reverse(3);
    reject(wire.encode());
    wire = new Wire();
    wire.cell(3, 0, 1, "0");
    valid(wire);
  }

  @Test
  void mapverify015ImmutableCountsRedactionAndFreshFailureIsolation() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    byte[] source = bytes(NORMAL);
    byte[] before = source.clone();
    var result = verifier.verify(source, NORMAL_HASH);
    assertThrows(UnsupportedOperationException.class, () -> result.put(PART_FILES, 9));
    assertArrayEquals(before, source);
    var malformed = new Wire();
    malformed.cell(0, 0, 1, "SYNTHETIC_FIXTURE_NOT_CREDENTIAL");
    reject(malformed.encode());
    assertEquals(TWO, verifier.verify(source, NORMAL_HASH));
    assertEquals("CurrentMigrationMappingVerifier[REDACTED]", verifier.toString());
  }

  @Test
  void mapverify016SharedVerifierHasFiniteIndependentSnapshots() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Map<String, Integer>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  byte[] source = bytes(NORMAL);
                  var result = verifier.verify(source, NORMAL_HASH);
                  source[0] = 0;
                  assertEquals(TWO, result);
                  return result;
                }));
      for (var future : futures) assertEquals(TWO, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.UTF_8);
  }

  private static String hash(byte[] data) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
  }

  private static void reject(byte[] data) throws Exception {
    reject(new CurrentMigrationMappingVerifier(), data, hash(data));
  }

  private static void reject(
      CurrentMigrationMappingVerifier verifier, byte[] data, String expected) {
    byte[] before = data == null ? null : data.clone();
    var failure =
        assertThrows(IllegalArgumentException.class, () -> verifier.verify(data, expected));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertArrayEquals(before, data);
  }

  private static void valid(Wire wire) throws Exception {
    byte[] data = wire.encode();
    assertEquals(TWO, new CurrentMigrationMappingVerifier().verify(data, hash(data)));
  }

  private static final class Wire {
    private final List<String> parts = new ArrayList<>(PARTS);
    private final Map<Integer, String> overrides = new HashMap<>();
    private String suffix = "";

    private String header(int index) throws Exception {
      String body = parts.get(index);
      byte[] data = bytes(body);
      String base =
          KINDS.get(index)
              + "\t"
              + (body.split("\n", -1).length - 2)
              + "\t"
              + data.length
              + "\t"
              + hash(data);
      return overrides.getOrDefault(index, base);
    }

    private void field(int index, int field, String value) throws Exception {
      String[] fields = header(index).split("\t", -1);
      fields[field] = value;
      overrides.put(index, String.join("\t", fields));
    }

    private void cell(int part, int row, int column, String value) {
      String[] lines = parts.get(part).split("\n", -1);
      String[] fields = lines[row + 1].split("\t", -1);
      fields[column] = value;
      lines[row + 1] = String.join("\t", fields);
      parts.set(part, String.join("\n", lines));
    }

    private void reverse(int part) {
      String[] lines = parts.get(part).split("\n", -1);
      var rows = new ArrayList<>(Arrays.asList(lines).subList(1, lines.length - 1));
      Collections.reverse(rows);
      parts.set(part, lines[0] + "\n" + String.join("\n", rows) + "\n");
    }

    private byte[] encode() throws Exception {
      var text = new StringBuilder(MAGIC);
      for (int index = 0; index < KINDS.size(); index++)
        text.append(header(index)).append('\n').append(parts.get(index));
      return bytes(text.append(suffix).toString());
    }
  }
}
