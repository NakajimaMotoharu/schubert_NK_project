package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-MUSICID001..012; fixed independent Python SHA256 vectors, never production expected
 * values.
 */
final class MusicLogicalIdTest {
  private static final String ASCII_PATH = "music/a.ogg";
  private static final String ASCII_A = "a";
  private static final String CANONICAL_E = "é";
  private static final String DECOMPOSED_E = "e\u0301";
  private static final String SUPPLEMENTARY = "𝄞";
  private static final String DIAGNOSTIC = "migration music logical ID input is invalid";
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String EXPECTED_ASCII =
      "0b9886db518de3252c15cefbe0e67016379c5fea7ee12a6d9c8c7f906efd3dcf";
  private static final String EXPECTED_JAPANESE =
      "ae90358a4e9bfb4593d592f221bd62411bffc9d85f997245c117dce405c47edc";
  private static final String EXPECTED_NFC =
      "a0e3ed7e4a5620e8d9050923635dba549756eb7575ad75dcefbe520bcb31ff33";
  private static final String EXPECTED_PAIRED =
      "0a5202230b75b53ae88582d923d197d17cabe1c3a993bfadd7f47da3f6964f1f";
  private static final String EXPECTED_ASCII_ONE =
      "22a27e0afc7c8a6ea339deacf3269de47cd71e59447b1714226cd990a5b5d971";
  private static final String EXPECTED_ASCII_MAX =
      "5e97c9e1d45f44b9658ec35dc52fe8a58cd6b3963ff09b0fe947d6aecf0c43a8";
  private static final String EXPECTED_NFC_MAX =
      "f602e736c9998298f44a0ffb312ab098a712cb00448b5614eb8bd052f38e677d";
  private static final String EXPECTED_SUPPLEMENTARY_MAX =
      "0564ecbbe255b5a8becc224a22b077fd71ac41592f1ffa5dd4f789e9ec0c4392";

  @Test
  void asciiPrefixAndUtf8MatchTheFixedIndependentSha256Vector() throws NoSuchAlgorithmException {
    assertEquals(EXPECTED_ASCII, new MusicLogicalId().fromDisplayPath(ASCII_PATH));
  }

  @Test
  void japanesePathUsesUtf8AndLowercase64Hex() throws NoSuchAlgorithmException {
    String result = new MusicLogicalId().fromDisplayPath("音楽/曲.flac");
    assertEquals(EXPECTED_JAPANESE, result);
    assertTrue(result.matches("[0-9a-f]{64}"));
  }

  @Test
  void canonicalAndDecomposedFormsUseTheSameFixedNfcVector() throws NoSuchAlgorithmException {
    var ids = new MusicLogicalId();
    assertEquals(EXPECTED_NFC, ids.fromDisplayPath(CANONICAL_E));
    assertEquals(EXPECTED_NFC, ids.fromDisplayPath(DECOMPOSED_E));
  }

  @Test
  void nullAndEmptyAreExplicitFixedInputFailures() {
    reject(null);
    reject("");
  }

  @Test
  void unpairedSurrogatesFailBeforeEncodingAndPairedScalarHasFixedVector()
      throws NoSuchAlgorithmException {
    reject("\ud800");
    reject("\udc00");
    assertEquals(EXPECTED_PAIRED, new MusicLogicalId().fromDisplayPath(SUPPLEMENTARY));
  }

  @Test
  void isoControlsCannotEnterTheHashedCanonicalDisplayMetadata() {
    for (String value : List.of("\u0000", "\t", "\n", "\r", "\b", "\f", "\u007f", "\u0085"))
      reject(ASCII_A + value);
  }

  @Test
  void asciiOneAnd512BytesHaveFixedVectorsWhile513IsRejected() throws NoSuchAlgorithmException {
    var ids = new MusicLogicalId();
    assertEquals(EXPECTED_ASCII_ONE, ids.fromDisplayPath(ASCII_A));
    assertEquals(EXPECTED_ASCII_MAX, ids.fromDisplayPath(ASCII_A.repeat(512)));
    reject(ASCII_A.repeat(513));
  }

  @Test
  void byteCeilingAppliesAfterNfcRatherThanToThe768ByteSource() throws NoSuchAlgorithmException {
    String source = DECOMPOSED_E.repeat(256);
    assertEquals(768, source.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(512, CANONICAL_E.repeat(256).getBytes(StandardCharsets.UTF_8).length);
    assertEquals(EXPECTED_NFC_MAX, new MusicLogicalId().fromDisplayPath(source));
    assertEquals(EXPECTED_NFC_MAX, new MusicLogicalId().fromDisplayPath(CANONICAL_E.repeat(256)));
    reject(CANONICAL_E.repeat(257));
  }

  @Test
  void supplementary128ScalarsAre512Utf8BytesRatherThan256Characters()
      throws NoSuchAlgorithmException {
    String maximum = SUPPLEMENTARY.repeat(128);
    assertEquals(512, maximum.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(EXPECTED_SUPPLEMENTARY_MAX, new MusicLogicalId().fromDisplayPath(maximum));
    reject(SUPPLEMENTARY.repeat(129));
  }

  @Test
  void caseWhitespaceSeparatorsAndPunctuationAreNotTrimmedOrRewritten()
      throws NoSuchAlgorithmException {
    var ids = new MusicLogicalId();
    var vectors =
        List.of(
            List.of("a", "22a27e0afc7c8a6ea339deacf3269de47cd71e59447b1714226cd990a5b5d971"),
            List.of("A", "0b5e0a998c8fb9958381cc9044d561d915cf8300a10b8e535dd64966b4dda823"),
            List.of(" a", "72bd7c9b5ebe10f2b43814f97ca5ae476dc5768364c16eebeafbaa322e4b8d7a"),
            List.of("a ", "6d13a580ae9c243044dc2c9479d5288c84d1b54a805a184df62a68ed149d9ae0"),
            List.of("a/b", "bd15593951c05abc4932d39ef3c41e6a6edf9ccb0673363653a6df9372104897"),
            List.of("a\\b", "c3e2a9eb9caa35f960e2afd92ca111935063e1da031617b67ca3766058bad814"),
            List.of("a.b", "63d09ddc5c61a3fdb0bc6ea9edfdb58811ee620479d998c3b75618e628006371"),
            List.of("a_b", "a349cf8547e71f758a2942e195669f7c550688b2b9150d245a3b3cb404df33ce"),
            List.of(" ", "2a8909b3d18256c82d8a0134097b9d8a6b29d49753f33fecdf5d76029c934126"));
    for (var vector : vectors) assertEquals(vector.get(1), ids.fromDisplayPath(vector.get(0)));
  }

  @Test
  void fixedRedactionAndIndependentSuccessDoNotRetainRejectedMetadata()
      throws NoSuchAlgorithmException {
    reject("private\u0000metadata");
    var ids = new MusicLogicalId();
    assertEquals("MusicLogicalId[REDACTED]", ids.toString());
    assertEquals(EXPECTED_ASCII, ids.fromDisplayPath(ASCII_PATH));
  }

  @Test
  void finiteWorkersUseFreshDigestsForTheSameStatelessIdentity()
      throws InterruptedException, ExecutionException, TimeoutException {
    var ids = new MusicLogicalId();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++)
        results.add(executor.submit(() -> ids.fromDisplayPath(ASCII_PATH)));
      for (var result : results)
        assertEquals(EXPECTED_ASCII, result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static void reject(@Nullable String value) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MusicLogicalId().fromDisplayPath(value))
            .getMessage());
  }
}
