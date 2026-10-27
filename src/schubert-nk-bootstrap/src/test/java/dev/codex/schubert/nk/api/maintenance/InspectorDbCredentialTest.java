package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-193..196: public encoding vectors, never credentials for an actual login. */
final class InspectorDbCredentialTest {
  private static final int MAX_INPUT_BYTES = 65536;

  @Test
  void validUtf8AndNewlines() {
    for (String value : List.of("A", " ASCII ", " あ\uD83D\uDE03e\u0301 ", "x".repeat(65536))) {
      for (String ending : List.of("", "\n", "\r\n")) {
        byte[] bytes = (value + ending).getBytes(StandardCharsets.UTF_8);
        if (bytes.length > MAX_INPUT_BYTES) continue;
        try (var material = InspectorDbCredential.consume(bytes)) {
          assertArrayEquals(new byte[bytes.length], bytes);
          char[] actual = material.copyPassword();
          assertArrayEquals(value.toCharArray(), actual);
          Arrays.fill(actual, '\0');
        }
      }
    }
  }

  @Test
  void invalidEncodingAndBounds() {
    assertThrows(NullPointerException.class, () -> InspectorDbCredential.consume(null));
    for (byte[] bytes :
        List.of(
            new byte[0],
            new byte[65537],
            new byte[] {(byte) 0xc0, (byte) 0xaf},
            new byte[] {(byte) 0xc2},
            new byte[] {(byte) 0xed, (byte) 0xa0, (byte) 0x80},
            new byte[] {(byte) 0xff},
            new byte[] {(byte) 0xf4, (byte) 0x90, (byte) 0x80, (byte) 0x80})) invalid(bytes);
    for (String value :
        List.of("\n", "\r\n", "\ufeffx", "x\u0000y", "x\ny", "x\ry", "x\r", "x\n\n", "x\r\r\n"))
      invalid(value.getBytes(StandardCharsets.UTF_8));
  }

  @Test
  void ownedCopiesAndClose() {
    var material = InspectorDbCredential.consume(new byte[] {65, 66, 67});
    try {
      char[] first = material.copyPassword();
      char[] second = material.copyPassword();
      assertNotSame(first, second);
      first[0] = 'Z';
      assertArrayEquals(new char[] {65, 66, 67}, second);
      assertEquals("InspectorDbCredential[REDACTED]", material.toString());
      material.close();
      material.close();
      var failure = assertThrows(IllegalStateException.class, material::copyPassword);
      assertEquals("inspector database credential is closed", failure.getMessage());
      assertNull(failure.getCause());
      assertArrayEquals(new char[] {65, 66, 67}, second);
      Arrays.fill(first, '\0');
      Arrays.fill(second, '\0');
    } finally {
      material.close();
    }
  }

  @Test
  void concurrentOwnership() throws Exception {
    var material = InspectorDbCredential.consume(new byte[] {65, 66, 67});
    try (var pool = Executors.newFixedThreadPool(12)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++)
        work.add(
            () -> {
              char[] actual = material.copyPassword();
              try {
                assertArrayEquals(new char[] {65, 66, 67}, actual);
                return true;
              } finally {
                Arrays.fill(actual, '\0');
              }
            });
      for (var done : pool.invokeAll(work)) assertTrue(done.get(5, TimeUnit.SECONDS));
      work.clear();
      for (int i = 0; i < 100; i++)
        work.add(
            () -> {
              try {
                char[] actual = material.copyPassword();
                try {
                  assertArrayEquals(new char[] {65, 66, 67}, actual);
                } finally {
                  Arrays.fill(actual, '\0');
                }
              } catch (IllegalStateException closed) {
                assertEquals("inspector database credential is closed", closed.getMessage());
              }
              return true;
            });
      var closing = pool.submit(material::close);
      for (var done : pool.invokeAll(work)) assertTrue(done.get(5, TimeUnit.SECONDS));
      closing.get(5, TimeUnit.SECONDS);
      assertThrows(IllegalStateException.class, material::copyPassword);
    } finally {
      material.close();
    }
  }

  private static void invalid(byte[] bytes) {
    var error =
        assertThrows(IllegalArgumentException.class, () -> InspectorDbCredential.consume(bytes));
    assertArrayEquals(new byte[bytes.length], bytes);
    assertEquals("inspector database credential format is invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
