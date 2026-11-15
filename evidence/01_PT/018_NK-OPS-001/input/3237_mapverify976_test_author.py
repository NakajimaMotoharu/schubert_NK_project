"""Independent framed mutation vectors; never call production code to construct expected bytes/hash."""
from pathlib import Path
import json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';g=json.loads((b/'evidence/PG33154-mapping958-source-v1/independent-golden-vectors.json').read_text());lit=lambda x:json.dumps(x,ensure_ascii=False);s='''package dev.codex.schubert.nk.migration;

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
  private static final String MAGIC = "NKMIGMAPPING1\\n";
  private static final String DIAGNOSTIC = "migration mapping serialization is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> KINDS = List.of("FILES", "ENTRIES", "SPEAKERS", "AUDIO");
  private static final Map<String, Integer> TWO = Map.of("FILES", 2, "ENTRIES", 2, "SPEAKERS", 2, "AUDIO", 2);
'''
for name,key in [('NORMAL','normal'),('EMPTY','empty'),('ONE_FILE','oneFile'),('BOUNDARY','boundary'),('OVERLAP','overlap')]:s+='  private static final String '+name+' = '+lit(g[key]['canonical'])+';\n  private static final String '+name+'_HASH = '+lit(g[key]['sha256'])+';\n'
s+='  private static final List<String> PARTS = List.of('+','.join(lit(x) for x in g['normal']['parts'])+');\n'
s+='''
  @Test
  void mapverify001FiveIndependentGoldenArtifactsAndCounts() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    assertEquals(TWO, verifier.verify(bytes(NORMAL), NORMAL_HASH));
    assertEquals(TWO, verifier.verify(bytes(BOUNDARY), BOUNDARY_HASH));
    assertEquals(TWO, verifier.verify(bytes(OVERLAP), OVERLAP_HASH));
    assertEquals(Map.of("FILES", 0, "ENTRIES", 0, "SPEAKERS", 0, "AUDIO", 0), verifier.verify(bytes(EMPTY), EMPTY_HASH));
    assertEquals(Map.of("FILES", 1, "ENTRIES", 0, "SPEAKERS", 0, "AUDIO", 0), verifier.verify(bytes(ONE_FILE), ONE_FILE_HASH));
    assertArrayEquals(bytes(NORMAL), new Wire().encode());
  }

  @Test
  void mapverify002MissingAndMalformedExpectedHashNeverNormalize() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier();
    reject(verifier, null, NORMAL_HASH);
    reject(verifier, bytes(NORMAL), null);
    for (String hash : List.of("", "A".repeat(64), "0".repeat(63), "0".repeat(65), "g".repeat(64), " " + NORMAL_HASH))
      reject(verifier, bytes(NORMAL), hash);
  }

  @Test
  void mapverify003WholeDigestMismatchAndInputAreUnchanged() throws Exception {
    byte[] changed = bytes(NORMAL); changed[changed.length - 1] = 0;
    reject(new CurrentMigrationMappingVerifier(), changed, NORMAL_HASH);
    reject(new CurrentMigrationMappingVerifier(), bytes(NORMAL), "0".repeat(64));
    byte[] source = bytes(NORMAL); byte[] before = source.clone();
    assertEquals(TWO, new CurrentMigrationMappingVerifier().verify(source, NORMAL_HASH));
    assertArrayEquals(before, source);
  }

  @Test
  void mapverify004MagicAndEveryShortPrefixFailEvenWithMatchingDigest() throws Exception {
    for (int length = 0; length <= bytes(MAGIC).length; length++) reject(Arrays.copyOf(bytes(NORMAL), length));
    byte[] wrong = bytes(NORMAL); wrong[0] = 'X'; reject(wrong);
  }

  @Test
  void mapverify005KindOrderUnknownDuplicateMissingAndTrailingBytes() throws Exception {
    for (int part = 0; part < KINDS.size(); part++)
      for (String kind : List.of("", "unknown", "files", KINDS.get((part + 1) % KINDS.size()))) {
        var wire = new Wire(); wire.field(part, 0, kind); reject(wire.encode());
      }
    var extra = new Wire(); extra.suffix = "X"; reject(extra.encode());
    extra.suffix = "\\n"; reject(extra.encode());
    byte[] normal = bytes(NORMAL); reject(Arrays.copyOf(normal, normal.length - 1));
  }

  @Test
  void mapverify006HeaderArityAsciiControlLengthAndNewline() throws Exception {
    for (String header : List.of("FILES", "FILES\\t0", "FILES\\t0\\t1", new Wire().header(0) + "\\tX",
        "X".repeat(96), "FILES\\r", "FILES" + (char) 0, "FILES" + (char) 127, "FILÉS")) {
      var wire = new Wire(); wire.overrides.put(0, header); reject(wire.encode());
    }
    reject(bytes(MAGIC + "FILES\\t"));
    byte[] high = bytes(NORMAL); high[bytes(MAGIC).length] = (byte) 0x80; reject(high);
  }

  @Test
  void mapverify007CountAndLengthCanonicalDecimalAndOverflow() throws Exception {
    for (int field : List.of(1, 2))
      for (String value : List.of("", "-1", "-0", "+1", "00", "01", "2147483648", "9223372036854775808",
          "-9223372036854775809", "99999999999999999999", "1.0", " 1", "1 ")) {
        var wire = new Wire(); wire.field(0, field, value); reject(wire.encode());
      }
    var huge = new Wire(); huge.field(2, 1, "2147483647"); huge.field(2, 2, "2147483647"); reject(huge.encode());
    huge = new Wire(); huge.field(0, 1, "2147483647"); reject(huge.encode());
  }

  @Test
  void mapverify008AllPartDigestFieldsAndPayloadBounds() throws Exception {
    for (int part = 0; part < KINDS.size(); part++) {
      for (String hash : List.of("", "A".repeat(64), "0".repeat(63), "0".repeat(65), "g".repeat(64), "0".repeat(64))) {
        var wire = new Wire(); wire.field(part, 3, hash); reject(wire.encode());
      }
      var shortBody = new Wire(); shortBody.field(part, 2, "2147483647"); reject(shortBody.encode());
    }
  }

  @Test
  void mapverify009ChildHeadersRowsColumnsLineLimitsAndControl() throws Exception {
    for (int part = 0; part < KINDS.size(); part++) {
      String childHeader = PARTS.get(part).split("\\n", -1)[0];
      for (String body : List.of("", "\\n", "wrong\\n", PARTS.get(part).stripTrailing(),
          childHeader + "\\n1\\n", childHeader + "\\n\\n", childHeader + "\\n" + "1".repeat(126) + "\\n",
          childHeader + "\\n1\\té\\t2\\n", childHeader + "\\n1\\t" + (char) 0 + "\\t2\\n",
          childHeader + "\\n1\\t" + (char) 127 + "\\t2\\n", childHeader + "\\n1\\t2\\r\\t3\\n")) {
        var wire = new Wire(); wire.parts.set(part, body); wire.field(part, 1, "0"); reject(wire.encode());
      }
      var wrongCount = new Wire(); wrongCount.field(part, 1, "1"); reject(wrongCount.encode());
      var wrongHeader = new Wire(); wrongHeader.parts.set(part, "X" + PARTS.get(part)); reject(wrongHeader.encode());
    }
  }

  @Test
  void mapverify010SignedLongLexicalAndUnsignedBounds() throws Exception {
    for (String value : List.of("", "-0", "+1", "00", "01", " 1", "1 ", "1.0", "x", "9223372036854775808", "-9223372036854775809")) {
      var wire = new Wire(); wire.cell(0, 0, 1, value); reject(wire.encode());
    }
    for (String value : List.of("-1", "2147483648")) {
      var wire = new Wire(); wire.cell(1, 0, 5, value); reject(wire.encode());
    }
    var max = new Wire(); max.cell(1, 0, 5, "2147483647"); valid(max);
  }

  @Test
  void mapverify011FileGamePkTargetOrderAndDerivedDisplayAreCanonical() throws Exception {
    for (String game : List.of("0", "3")) { var wire = new Wire(); wire.cell(0, 0, 0, game); reject(wire.encode()); }
    for (String id : List.of("0", "1000000000000")) { var wire = new Wire(); wire.cell(0, 0, 2, id); reject(wire.encode()); }
    var duplicate = new Wire(); duplicate.cell(0, 1, 2, "101"); reject(duplicate.encode());
    duplicate = new Wire(); duplicate.cell(0, 1, 0, "1"); duplicate.cell(0, 1, 1, "-5"); reject(duplicate.encode());
    var order = new Wire(); order.reverse(0); reject(order.encode());
    order = new Wire(); order.cell(0, 0, 3, "2"); reject(order.encode());
    var qualifiedCurrent = new Wire(); qualifiedCurrent.cell(0, 1, 1, "-5"); valid(qualifiedCurrent);
  }

  @Test
  void mapverify012EntryFileGamePkOrderIndexAndIndependentTargets() throws Exception {
    var wire = new Wire(); wire.cell(1, 0, 4, "999"); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 0, 3, "2"); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 1, 0, "-10"); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 1, 1, "201"); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 0, 2, "2"); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 1, 3, "1"); wire.cell(1, 1, 4, "101"); reject(wire.encode());
    wire = new Wire(); wire.reverse(1); reject(wire.encode());
    wire = new Wire(); wire.cell(1, 0, 1, "901"); wire.cell(1, 1, 1, "201"); valid(wire);
  }

  @Test
  void mapverify013SpeakerPkGameTargetAndCurrentCanonicalOrder() throws Exception {
    for (String game : List.of("0", "3")) { var wire = new Wire(); wire.cell(2, 0, 0, game); reject(wire.encode()); }
    for (String id : List.of("0", "1000000000000")) { var wire = new Wire(); wire.cell(2, 0, 2, id); reject(wire.encode()); }
    var wire = new Wire(); wire.cell(2, 1, 1, "-3"); reject(wire.encode());
    wire = new Wire(); wire.cell(2, 1, 2, "1"); reject(wire.encode());
    wire = new Wire(); wire.reverse(2); reject(wire.encode());
    wire = new Wire(); wire.cell(2, 0, 2, "6"); wire.cell(2, 1, 2, "1"); valid(wire);
  }

  @Test
  void mapverify014AudioGameN12AndStrictCurrentAndTargetOrder() throws Exception {
    for (String game : List.of("0", "3")) { var wire = new Wire(); wire.cell(3, 0, 0, game); reject(wire.encode()); }
    for (String id : List.of("0", "1000000000000")) { var wire = new Wire(); wire.cell(3, 0, 2, id); reject(wire.encode()); }
    var wire = new Wire(); wire.cell(3, 1, 1, "-5"); reject(wire.encode());
    wire = new Wire(); wire.cell(3, 1, 2, "21"); reject(wire.encode());
    wire = new Wire(); wire.cell(3, 1, 2, "20"); reject(wire.encode());
    wire = new Wire(); wire.reverse(3); reject(wire.encode());
    wire = new Wire(); wire.cell(3, 0, 1, "0"); valid(wire);
  }

  @Test
  void mapverify015ImmutableCountsRedactionAndFreshFailureIsolation() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier(); byte[] source = bytes(NORMAL); byte[] before = source.clone();
    var result = verifier.verify(source, NORMAL_HASH);
    assertThrows(UnsupportedOperationException.class, () -> result.put("FILES", 9));
    assertArrayEquals(before, source);
    var malformed = new Wire(); malformed.cell(0, 0, 1, "SYNTHETIC_FIXTURE_NOT_CREDENTIAL"); reject(malformed.encode());
    assertEquals(TWO, verifier.verify(source, NORMAL_HASH));
    assertEquals("CurrentMigrationMappingVerifier[REDACTED]", verifier.toString());
  }

  @Test
  void mapverify016SharedVerifierHasFiniteIndependentSnapshots() throws Exception {
    var verifier = new CurrentMigrationMappingVerifier(); var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Map<String, Integer>>>();
      for (int index = 0; index < TASKS; index++) futures.add(executor.submit(() -> {
        byte[] source = bytes(NORMAL); var result = verifier.verify(source, NORMAL_HASH); source[0] = 0;
        assertEquals(TWO, result); return result;
      }));
      for (var future : futures) assertEquals(TWO, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow(); assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static byte[] bytes(String text) { return text.getBytes(StandardCharsets.UTF_8); }
  private static String hash(byte[] data) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
  }
  private static void reject(byte[] data) throws Exception {
    reject(new CurrentMigrationMappingVerifier(), data, hash(data));
  }
  private static void reject(CurrentMigrationMappingVerifier verifier, byte[] data, String expected) {
    byte[] before = data == null ? null : data.clone();
    var failure = assertThrows(IllegalArgumentException.class, () -> verifier.verify(data, expected));
    assertEquals(DIAGNOSTIC, failure.getMessage()); assertNull(failure.getCause()); assertArrayEquals(before, data);
  }
  private static void valid(Wire wire) throws Exception {
    byte[] data = wire.encode(); assertEquals(TWO, new CurrentMigrationMappingVerifier().verify(data, hash(data)));
  }

  private static final class Wire {
    private final List<String> parts = new ArrayList<>(PARTS);
    private final Map<Integer, String> overrides = new HashMap<>();
    private String suffix = "";
    private String header(int index) throws Exception {
      String body = parts.get(index); byte[] data = bytes(body);
      String base = KINDS.get(index) + "\\t" + (body.split("\\n", -1).length - 2) + "\\t" + data.length + "\\t" + hash(data);
      return overrides.getOrDefault(index, base);
    }
    private void field(int index, int field, String value) throws Exception {
      String[] fields = header(index).split("\\t", -1); fields[field] = value; overrides.put(index, String.join("\\t", fields));
    }
    private void cell(int part, int row, int column, String value) {
      String[] lines = parts.get(part).split("\\n", -1); String[] fields = lines[row + 1].split("\\t", -1);
      fields[column] = value; lines[row + 1] = String.join("\\t", fields); parts.set(part, String.join("\\n", lines));
    }
    private void reverse(int part) {
      String[] lines = parts.get(part).split("\\n", -1);
      var rows = new ArrayList<>(Arrays.asList(lines).subList(1, lines.length - 1)); Collections.reverse(rows);
      parts.set(part, lines[0] + "\\n" + String.join("\\n", rows) + "\\n");
    }
    private byte[] encode() throws Exception {
      var text = new StringBuilder(MAGIC);
      for (int index = 0; index < KINDS.size(); index++) text.append(header(index)).append('\\n').append(parts.get(index));
      return bytes(text.append(suffix).toString());
    }
  }
}
'''
p=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentMigrationMappingVerifierTest.java';assert not p.exists();p.open('x').write(s)
p=p.with_name('CurrentMigrationMappingManifestTest.java');s=p.read_text();anchor='  private record Inputs(';assert s.count(anchor)==1;methods='''  @Test
  void mapman009SerializedReadbackUsesRetainedDeclaredDigest() throws Exception {
    var declared = inputs(false, false, false).manifest();
    declared.verifySerialized(NORMAL.getBytes(StandardCharsets.US_ASCII));
    assertEquals(NORMAL_HASH, declared.sha256());
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), declared.canonicalBytes());
  }

  @Test
  void mapman010OtherValidManifestNullAndCorruptBytesCannotBorrowExpectedHash() throws Exception {
    var declared = inputs(false, false, false).manifest();
    assertThrows(IllegalArgumentException.class, () -> declared.verifySerialized(null));
    assertThrows(IllegalArgumentException.class, () -> declared.verifySerialized(EMPTY.getBytes(StandardCharsets.US_ASCII)));
    byte[] corrupt = NORMAL.getBytes(StandardCharsets.US_ASCII); corrupt[0] = 0;
    assertThrows(IllegalArgumentException.class, () -> declared.verifySerialized(corrupt));
    assertEquals(NORMAL_HASH, declared.sha256());
  }

''';s=s.replace('PT-MIG-MAPMAN001..008','PT-MIG-MAPMAN001..010').replace(anchor,methods+anchor);p.write_text(s);print('created16 verifier +2 manifest tests; no runtime/IO')
