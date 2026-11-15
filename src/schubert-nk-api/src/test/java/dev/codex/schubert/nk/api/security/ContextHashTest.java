package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.security.NoSuchAlgorithmException;
import java.security.Provider;
import java.security.Security;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.parallel.Isolated;

/**
 * PT-AUT-005-H01: vectors independently calculated by Python hashlib SHA-256 over 64 ASCII bytes.
 */
@Isolated("Temporarily remove JCA providers to verify fail-closed startup")
@Timeout(value = 20, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class ContextHashTest {
  @Test
  void bug036CallerMonitorCannotBlockSharedDigest() throws Exception {
    ContextHash hashes = new ContextHash();
    var executor = Executors.newVirtualThreadPerTaskExecutor();
    try {
      synchronized (hashes) {
        assertEquals(
            "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb",
            executor
                .submit(() -> hashes.calculate(AuthenticationContext.of("a".repeat(64))))
                .get(5, java.util.concurrent.TimeUnit.SECONDS));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }

  @Test
  void asciiVectorsAndConcurrentCallsDoNotShareDigestState() throws Exception {
    ContextHash hashes = new ContextHash();
    String[] expected = {
      "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb",
      "a0fab1377f49a759b57f63318262ebe89fabfc990e8e93ceac2984561482b9d4"
    };
    AuthenticationContext[] input = {
      AuthenticationContext.of("a".repeat(64)), AuthenticationContext.of("b".repeat(64))
    };
    var executor = Executors.newVirtualThreadPerTaskExecutor();
    try {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 100; i++) {
        int index = i % 2;
        futures.add(executor.submit(() -> hashes.calculate(input[index])));
      }
      for (int i = 0; i < futures.size(); i++)
        assertEquals(expected[i % 2], futures.get(i).get(5, java.util.concurrent.TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertThrows(NullPointerException.class, () -> hashes.calculate(null));
    assertFalse(hashes.toString().contains(expected[0]));
    for (String malformed :
        new String[] {"", "a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64)}) {
      assertThrows(IllegalArgumentException.class, () -> AuthenticationContext.of(malformed));
    }
  }

  @Test
  void unavailableMandatoryDigestPreventsStartupAndRestoresProviders() {
    Provider[] original = Security.getProviders();
    try {
      for (Provider provider : original) Security.removeProvider(provider.getName());
      assertThrows(NoSuchAlgorithmException.class, ContextHash::new);
    } finally {
      for (int index = 0; index < original.length; index++)
        Security.insertProviderAt(original[index], index + 1);
    }
    assertArrayEquals(original, Security.getProviders());
  }

  @Test
  void hashOwn001DigestAndFormatFailuresEraseOwnedBytesAndReleasePrivateLock() throws Exception {
    String golden = "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
    for (boolean failDigest : new boolean[] {true, false}) {
      for (Throwable fault :
          new Throwable[] {
            new AssertionError("synthetic hash fault"),
            new IllegalArgumentException("synthetic hash fault")
          }) {
        byte[][] captured = new byte[2][];
        int[] calls = new int[2];
        var digest = java.security.MessageDigest.getInstance("SHA-256");
        var operations =
            new ContextHash.DigestOperations() {
              @Override
              public byte[] digest(byte[] raw) {
                captured[0] = raw;
                calls[0]++;
                if (failDigest && calls[0] == 1) throwHashFault(fault);
                captured[1] = digest.digest(raw);
                return captured[1];
              }

              @Override
              public String format(byte[] hashed) {
                calls[1]++;
                if (!failDigest && calls[1] == 1) throwHashFault(fault);
                return java.util.HexFormat.of().formatHex(hashed);
              }
            };
        var hashes = new ContextHash(operations);
        var context = AuthenticationContext.of("a".repeat(64));
        Throwable observed = assertThrows(fault.getClass(), () -> hashes.calculate(context));
        org.junit.jupiter.api.Assertions.assertSame(fault, observed);
        assertArrayEquals(new byte[64], captured[0]);
        if (failDigest) org.junit.jupiter.api.Assertions.assertNull(captured[1]);
        else assertArrayEquals(new byte[32], captured[1]);
        assertEquals("a".repeat(64), context.wireValue());
        byte[] firstRaw = captured[0];
        byte[] firstHash = captured[1];
        var executor = Executors.newSingleThreadExecutor();
        try {
          assertEquals(
              golden,
              executor
                  .submit(() -> hashes.calculate(context))
                  .get(5, java.util.concurrent.TimeUnit.SECONDS));
        } finally {
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
        }
        assertEquals(2, calls[0]);
        assertEquals(failDigest ? 1 : 2, calls[1]);
        org.junit.jupiter.api.Assertions.assertNotSame(firstRaw, captured[0]);
        if (!failDigest) org.junit.jupiter.api.Assertions.assertNotSame(firstHash, captured[1]);
        assertArrayEquals(new byte[64], captured[0]);
        assertArrayEquals(new byte[32], captured[1]);
        assertEquals("a".repeat(64), context.wireValue());
      }
    }
  }

  @Test
  void hashOwn002NullOperationsFailBeforeAnySecretAcquisition() {
    assertThrows(NullPointerException.class, () -> new ContextHash(null));
  }

  @Test
  void hashOwn003AsciiAndDigestBoundariesUseFixedVectorAndDoNotBorrowCallerMonitor()
      throws Exception {
    String golden = "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
    byte[] expectedAscii = new byte[64];
    java.util.Arrays.fill(expectedAscii, (byte) 'a');
    byte[] expectedHash = java.util.HexFormat.of().parseHex(golden);
    byte[][] captured = new byte[2][];
    int[] calls = new int[2];
    var digest = java.security.MessageDigest.getInstance("SHA-256");
    var operations =
        new ContextHash.DigestOperations() {
          @Override
          public byte[] digest(byte[] raw) {
            assertArrayEquals(expectedAscii, raw);
            captured[0] = raw;
            calls[0]++;
            return digest.digest(raw);
          }

          @Override
          public String format(byte[] hashed) {
            assertArrayEquals(expectedHash, hashed);
            captured[1] = hashed;
            calls[1]++;
            return java.util.HexFormat.of().formatHex(hashed);
          }
        };
    var hashes = new ContextHash(operations);
    var context = AuthenticationContext.of("a".repeat(64));
    var executor = Executors.newSingleThreadExecutor();
    try {
      synchronized (hashes) {
        assertEquals(
            golden,
            executor
                .submit(() -> hashes.calculate(context))
                .get(5, java.util.concurrent.TimeUnit.SECONDS));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertArrayEquals(new int[] {1, 1}, calls);
    assertArrayEquals(new byte[64], captured[0]);
    assertArrayEquals(new byte[32], captured[1]);
    assertArrayEquals(
        expectedAscii, "a".repeat(64).getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    assertEquals("a".repeat(64), context.wireValue());
    assertEquals(32, expectedHash.length);
  }

  private static void throwHashFault(Throwable failure) {
    if (failure instanceof Error fatal) throw fatal;
    throw (RuntimeException) failure;
  }
}
