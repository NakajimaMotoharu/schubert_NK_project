package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * PT-DB-INBOX-105..112; PG-D-131; independent byte assembly, runtime keys, no saved credentials.
 */
final class InspectorAesCredentialTest {
  @Test
  void validKeyAndVersionBounds() {
    for (String version : List.of("v", "Abcdef0123456789", "v1-._test", "9")) {
      byte[] expected = key(32);
      byte[] input = envelope(version, expected);
      try (var material = InspectorAesCredential.consume(input)) {
        assertEquals(version, material.version());
        byte[] copy = material.copyKey();
        try {
          assertArrayEquals(expected, copy);
        } finally {
          Arrays.fill(copy, (byte) 0);
        }
        assertArrayEquals(new byte[input.length], input);
        assertEquals(
            "InspectorAesCredential[version=" + version + ", key=<redacted>, closed=false]",
            material.toString());
      } finally {
        Arrays.fill(expected, (byte) 0);
      }
    }
  }

  @Test
  void envelopeLengthAndMagic() {
    byte[] key = key(32);
    try {
      for (int size : new int[] {0, 1, 7, 53, 70, 1000}) bad(new byte[size]);
      for (int position = 0; position < 7; position++) {
        byte[] input = envelope("v1", key);
        input[position] = '?';
        bad(input);
      }
      byte[] base = envelope("v1", key);
      bad(Arrays.copyOf(base, base.length - 1));
      bad(Arrays.copyOf(base, base.length + 1));
      byte[] bom = new byte[base.length + 3];
      System.arraycopy(base, 0, bom, 3, base.length);
      bom[0] = (byte) 0xef;
      bom[1] = (byte) 0xbb;
      bom[2] = (byte) 0xbf;
      bad(bom);
      byte[] crlf = new byte[base.length + 1];
      System.arraycopy(base, 0, crlf, 0, base.length - 1);
      crlf[crlf.length - 2] = '\r';
      crlf[crlf.length - 1] = '\n';
      bad(crlf);
      Arrays.fill(base, (byte) 0);
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  @Test
  void versionAndLineBoundaries() {
    byte[] key = key(32);
    try {
      for (String version :
          List.of(
              "",
              "abcdefghijklmnopq",
              "-v",
              "_v",
              ".v",
              "v v",
              "v:v",
              "v\tv",
              "v\nv",
              "v\0v",
              "あ",
              "é")) bad(envelope(version, key));
      byte[] input = envelope("v1", key);
      input[9] = '\r';
      bad(input);
      input = envelope("v1", key);
      input[input.length - 1] = '\r';
      bad(input);
      input = envelope("v1", key);
      input[8] = (byte) 0xff;
      bad(input);
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  @Test
  void base64AndKeySize() {
    for (int size : new int[] {0, 1, 30, 31, 33, 34, 64}) {
      byte[] key = key(size);
      try {
        bad(envelope("v1", key));
      } finally {
        Arrays.fill(key, (byte) 0);
      }
    }
    byte[] key = key(32);
    try {
      for (byte value : new byte[] {'.', ' ', '\t', '\n', '=', (byte) 0xff}) {
        byte[] input = envelope("v1", key);
        input[12] = value;
        bad(input);
      }
      byte[] input = envelope("v1", key);
      input[input.length - 2] = 'A';
      bad(input);
      input = envelope("v1", key);
      String alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
      int pos = input.length - 3;
      int index = alphabet.indexOf(input[pos]);
      assertEquals(0, index % 4);
      input[pos] =
          (byte) alphabet.charAt(index + 1); // same decoded32, noncanonical low padding bits
      bad(input);
      input = envelope("v1", key);
      byte[] unpadded = new byte[input.length - 1];
      System.arraycopy(input, 0, unpadded, 0, input.length - 2);
      unpadded[unpadded.length - 1] = '\n';
      Arrays.fill(input, (byte) 0);
      bad(unpadded);
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  @Test
  void consumedInputAndCopiedKeysDoNotAlias() {
    byte[] expected = key(32);
    byte[] input = envelope("v1", expected);
    var material = InspectorAesCredential.consume(input);
    try {
      assertArrayEquals(new byte[input.length], input);
      Arrays.fill(input, (byte) 'Z');
      byte[] first = material.copyKey();
      assertArrayEquals(expected, first);
      Arrays.fill(first, (byte) 0);
      byte[] second = material.copyKey();
      assertArrayEquals(expected, second);
      assertNotSame(first, second);
      material.close();
      assertArrayEquals(expected, second); // caller owns it; destructor cannot mutate external copy
      Arrays.fill(second, (byte) 0);
      assertThrows(IllegalStateException.class, material::copyKey);
    } finally {
      material.close();
      Arrays.fill(expected, (byte) 0);
      Arrays.fill(input, (byte) 0);
    }
  }

  @Test
  void closeIsIdempotentAndRedacted() {
    byte[] key = key(32);
    var material = InspectorAesCredential.consume(envelope("v1", key));
    String encoded = Base64.getEncoder().encodeToString(key);
    assertFalse(material.toString().contains(encoded));
    material.close();
    material.close();
    var error = assertThrows(IllegalStateException.class, material::copyKey);
    assertEquals("inspector AES credential is closed", error.getMessage());
    assertNull(error.getCause());
    assertEquals("v1", material.version());
    assertEquals(
        "InspectorAesCredential[version=v1, key=<redacted>, closed=true]", material.toString());
    Arrays.fill(key, (byte) 0);
  }

  @Test
  void concurrentCopiesAndCloseStayConsistent() throws Exception {
    try (var pool = Executors.newFixedThreadPool(12)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        int index = i;
        tasks.add(
            () -> {
              byte[] expected = key(32);
              byte[] input = envelope("v" + index, expected);
              try (var material = InspectorAesCredential.consume(input)) {
                assertArrayEquals(new byte[input.length], input);
                assertEquals("v" + index, material.version());
                byte[] copy = material.copyKey();
                assertArrayEquals(expected, copy);
                Arrays.fill(copy, (byte) 0);
                return true;
              } finally {
                Arrays.fill(expected, (byte) 0);
              }
            });
      }
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get(5, TimeUnit.SECONDS));
      byte[] expected = key(32);
      var material = InspectorAesCredential.consume(envelope("race", expected));
      try {
        // Caller holding the public object's monitor must not block its private state lock.
        synchronized (material) {
          byte[] copy = pool.submit(material::copyKey).get(5, TimeUnit.SECONDS);
          assertArrayEquals(expected, copy);
          Arrays.fill(copy, (byte) 0);
        }
        var start = new CountDownLatch(1);
        tasks.clear();
        for (int i = 0; i < 100; i++)
          tasks.add(
              () -> {
                start.await();
                try {
                  byte[] copy = material.copyKey();
                  assertArrayEquals(expected, copy);
                  Arrays.fill(copy, (byte) 0);
                } catch (IllegalStateException closed) {
                  assertEquals("inspector AES credential is closed", closed.getMessage());
                }
                return true;
              });
        var futures = new ArrayList<Future<Boolean>>();
        for (var task : tasks) futures.add(pool.submit(task));
        start.countDown();
        material.close();
        for (var result : futures) assertTrue(result.get(5, TimeUnit.SECONDS));
        assertThrows(IllegalStateException.class, material::copyKey);
      } finally {
        material.close();
        Arrays.fill(expected, (byte) 0);
      }
    }
  }

  @Test
  void nullAndInvalidInputsNeverEscape() {
    assertThrows(NullPointerException.class, () -> InspectorAesCredential.consume(null));
    byte[] key = key(32);
    try {
      byte[] input = envelope("v1", key);
      input[10] = '?';
      String encoded = Base64.getEncoder().encodeToString(key);
      var error =
          assertThrows(IllegalArgumentException.class, () -> InspectorAesCredential.consume(input));
      assertEquals("inspector AES credential format is invalid", error.getMessage());
      assertFalse(error.toString().contains(encoded));
      assertNull(error.getCause());
      assertEquals(0, error.getSuppressed().length);
      assertArrayEquals(new byte[input.length], input);
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  private static byte[] key(int size) {
    byte[] value = new byte[size];
    new SecureRandom().nextBytes(value);
    return value;
  }

  private static byte[] envelope(String version, byte[] key) {
    byte[] prefix = ("NKKEY1\n" + version + "\n").getBytes(StandardCharsets.UTF_8);
    byte[] encoded = Base64.getEncoder().encode(key);
    byte[] result = Arrays.copyOf(prefix, prefix.length + encoded.length + 1);
    System.arraycopy(encoded, 0, result, prefix.length, encoded.length);
    result[result.length - 1] = '\n';
    Arrays.fill(encoded, (byte) 0);
    return result;
  }

  private static void bad(byte[] input) {
    var error =
        assertThrows(IllegalArgumentException.class, () -> InspectorAesCredential.consume(input));
    assertEquals("inspector AES credential format is invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertArrayEquals(new byte[input.length], input);
  }
}
