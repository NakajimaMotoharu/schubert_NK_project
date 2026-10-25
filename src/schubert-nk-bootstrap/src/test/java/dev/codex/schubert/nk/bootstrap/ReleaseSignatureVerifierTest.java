package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** RFC8032 TEST1/2 public values only; neither private keys nor production-generated expected. */
final class ReleaseSignatureVerifierTest {
  private static final String PREFIX = "302a300506032b6570032100";
  private static final String PUBLIC1 =
      "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a";
  private static final String SIGN1 =
      "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b";
  private static final String PUBLIC2 =
      "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c";
  private static final String SIGN2 =
      "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00";

  private static byte[] hex(String s) {
    return HexFormat.of().parseHex(s);
  }

  private static ReleaseSignatureVerifier first() {
    return new ReleaseSignatureVerifier(hex(PREFIX + PUBLIC1));
  }

  @Test
  void sign001IndependentRfcVectors() throws Exception {
    first().verify(new byte[0], hex(SIGN1));
    new ReleaseSignatureVerifier(hex(PREFIX + PUBLIC2)).verify(hex("72"), hex(SIGN2));
  }

  @Test
  void sign002MessageSignatureAndWrongKey() {
    assertThrows(IOException.class, () -> first().verify(hex("01"), hex(SIGN1)));
    byte[] corrupted = hex(SIGN1);
    corrupted[0] ^= 1;
    assertThrows(IOException.class, () -> first().verify(new byte[0], corrupted));
    assertThrows(IOException.class, () -> first().verify(hex("72"), hex(SIGN2)));
  }

  @Test
  void sign003DerAndNullContracts() {
    assertThrows(NullPointerException.class, () -> new ReleaseSignatureVerifier(null));
    assertThrows(
        NullPointerException.class,
        () -> new ReleaseSignatureVerifier(hex(PREFIX + PUBLIC1), null));
    assertThrows(NullPointerException.class, () -> first().verify(null, hex(SIGN1)));
    assertThrows(NullPointerException.class, () -> first().verify(new byte[0], null));
    for (int length : List.of(0, 43, 45))
      assertThrows(
          IllegalArgumentException.class, () -> new ReleaseSignatureVerifier(new byte[length]));
    for (int i = 0; i < 12; i++) {
      byte[] key = hex(PREFIX + PUBLIC1);
      key[i] ^= 1;
      assertThrows(IllegalArgumentException.class, () -> new ReleaseSignatureVerifier(key));
    }
  }

  @Test
  void sign004MaterialBoundaries() {
    for (int length : List.of(0, 63, 65))
      assertThrows(
          IllegalArgumentException.class, () -> first().verify(new byte[0], new byte[length]));
    assertThrows(
        IllegalArgumentException.class, () -> first().verify(new byte[1_048_577], hex(SIGN1)));
    // Bounded material reaches real verification, and is independently not RFC TEST1's message.
    assertThrows(IOException.class, () -> first().verify(new byte[1_048_576], hex(SIGN1)));
  }

  @Test
  void sign005SnapshotAndErasedOwnedBuffers() throws Exception {
    byte[] inputKey = hex(PREFIX + PUBLIC1);
    byte[] message = hex("72");
    byte[] signature = hex(SIGN2);
    var retained = new AtomicReference<List<byte[]>>();
    var subject =
        new ReleaseSignatureVerifier(
            inputKey,
            (k, m, s) -> {
              assertArrayEquals(hex(PREFIX + PUBLIC1), k);
              assertArrayEquals(hex("72"), m);
              assertArrayEquals(hex(SIGN2), s);
              retained.set(List.of(k, m, s));
              return true;
            });
    Arrays.fill(inputKey, (byte) 0);
    subject.verify(message, signature);
    for (byte[] owned : retained.get()) assertArrayEquals(new byte[owned.length], owned);
    assertArrayEquals(hex("72"), message);
    assertArrayEquals(hex(SIGN2), signature);
  }

  @Test
  void sign006KnownCryptoFailureIsRedacted() {
    var retained = new AtomicReference<List<byte[]>>();
    var subject =
        new ReleaseSignatureVerifier(
            hex(PREFIX + PUBLIC1),
            (k, m, s) -> {
              retained.set(List.of(k, m, s));
              throw new GeneralSecurityException("PRIVATE");
            });
    IOException actual =
        assertThrows(IOException.class, () -> subject.verify(hex("72"), hex(SIGN2)));
    assertEquals("release signature unavailable", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
    for (byte[] owned : retained.get()) assertArrayEquals(new byte[owned.length], owned);
  }

  @Test
  void sign007UnknownFailureIdentityAndErasure() {
    for (Throwable failure :
        List.of(new IllegalStateException("PRIVATE"), new AssertionError("PRIVATE"))) {
      var retained = new AtomicReference<List<byte[]>>();
      var subject =
          new ReleaseSignatureVerifier(
              hex(PREFIX + PUBLIC1),
              (k, m, s) -> {
                retained.set(List.of(k, m, s));
                if (failure instanceof RuntimeException e) throw e;
                throw (Error) failure;
              });
      assertSame(
          failure, assertThrows(Throwable.class, () -> subject.verify(hex("72"), hex(SIGN2))));
      for (byte[] owned : retained.get()) assertArrayEquals(new byte[owned.length], owned);
    }
  }

  @Test
  void sign008ConcurrentNativeProviderAndMalformedPoint() throws Exception {
    var subject = first();
    var barrier = new CyclicBarrier(4);
    try (var executor = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            executor.submit(
                () -> {
                  barrier.await(5, TimeUnit.SECONDS);
                  subject.verify(new byte[0], hex(SIGN1));
                  assertThrows(IOException.class, () -> subject.verify(hex("01"), hex(SIGN1)));
                  return true;
                }));
      for (var future : futures) assertTrue(future.get(5, TimeUnit.SECONDS));
    }
    assertThrows(
        IOException.class,
        () ->
            new ReleaseSignatureVerifier(hex(PREFIX + "ff".repeat(32)))
                .verify(new byte[0], hex(SIGN1)));
    assertThrows(IOException.class, () -> subject.verify(new byte[0], hex("ff".repeat(64))));
  }
}
