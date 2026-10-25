package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.security.NoSuchAlgorithmException;
import java.security.Provider;
import java.security.Security;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Isolated;

/**
 * PT-AUT-005-H01: vectors independently calculated by Python hashlib SHA-256 over 64 ASCII bytes.
 */
@Isolated("Temporarily remove JCA providers to verify fail-closed startup")
final class ContextHashTest {
  @Test
  void bug036CallerMonitorCannotBlockSharedDigest() throws Exception {
    ContextHash hashes = new ContextHash();
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      synchronized (hashes) {
        assertEquals(
            "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb",
            executor
                .submit(() -> hashes.calculate(AuthenticationContext.of("a".repeat(64))))
                .get(5, java.util.concurrent.TimeUnit.SECONDS));
      }
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
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 100; i++) {
        int index = i % 2;
        futures.add(executor.submit(() -> hashes.calculate(input[index])));
      }
      for (int i = 0; i < futures.size(); i++) assertEquals(expected[i % 2], futures.get(i).get());
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
}
