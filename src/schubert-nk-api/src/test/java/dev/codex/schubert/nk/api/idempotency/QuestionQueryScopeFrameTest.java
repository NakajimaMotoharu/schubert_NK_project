package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-QRY-SCOPE-001/003; SSC157 independent eight-byte literals and caller ownership. */
final class QuestionQueryScopeFrameTest {
  @Test
  void scope001LiteralFramesAndInspectionOnlyLegacyAreCallerOwned() {
    byte[] wire = new byte[256];
    Arrays.fill(wire, (byte) ' ');
    for (Role role : Role.values()) {
      byte[] expected = new byte[264];
      byte[] prefix =
          HexFormat.of().parseHex(role == Role.USER ? "4e4b515259310055" : "4e4b515259310041");
      System.arraycopy(prefix, 0, expected, 0, 8);
      Arrays.fill(expected, 8, expected.length, (byte) ' ');
      byte[] frame = QuestionQueryScopeFrame.wrap(role, wire);
      assertArrayEquals(expected, frame);
      assertEquals(role, QuestionQueryScopeFrame.capturedScope(frame));
      for (String layout : new String[] {"QSSRSP01", "QSDRSP01"}) {
        byte[] inspected =
            QuestionQueryScopeFrame.wireForInspection(identity(layout, "001"), frame);
        assertArrayEquals(wire, inspected);
        inspected[0] = 0;
        assertEquals(' ', frame[8]);
      }
      frame[8] = 0;
      assertEquals(' ', wire[0]);
    }
    for (byte[] old : new byte[][] {wire, new byte[0], new byte[6]}) {
      byte[] inspected =
          QuestionQueryScopeFrame.wireForInspection(identity("NTDRSP01", "001"), old);
      assertArrayEquals(old, inspected);
      assertNotSame(old, inspected);
      assertThrows(
          IllegalArgumentException.class, () -> QuestionQueryScopeFrame.capturedScope(old));
    }
  }

  @Test
  void scope003NullUnknownScopeTruncationMagicAndCrossRouteAreNeverGranted() {
    byte[] frame = QuestionQueryScopeFrame.wrap(Role.ADMIN, new byte[256]);
    assertThrows(
        NullPointerException.class, () -> QuestionQueryScopeFrame.wrap(null, new byte[256]));
    assertThrows(NullPointerException.class, () -> QuestionQueryScopeFrame.wrap(Role.USER, null));
    assertThrows(NullPointerException.class, () -> QuestionQueryScopeFrame.capturedScope(null));
    assertThrows(
        NullPointerException.class, () -> QuestionQueryScopeFrame.wireForInspection(null, frame));
    assertThrows(
        NullPointerException.class,
        () -> QuestionQueryScopeFrame.wireForInspection(identity("QSSRSP01", "001"), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionQueryScopeFrame.wrap(Role.USER, new byte[255]));
    for (int length : new int[] {0, 6, 7, 8, 263}) {
      byte[] shortFrame = Arrays.copyOf(frame, length);
      assertThrows(
          IllegalArgumentException.class, () -> QuestionQueryScopeFrame.capturedScope(shortFrame));
    }
    byte[] unknown = frame.clone();
    unknown[7] = 'X';
    assertThrows(
        IllegalArgumentException.class, () -> QuestionQueryScopeFrame.capturedScope(unknown));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionQueryScopeFrame.wireForInspection(identity("QSSRSP01", "001"), unknown));
    byte[] magic = frame.clone();
    magic[0] = 'X';
    assertThrows(
        IllegalArgumentException.class, () -> QuestionQueryScopeFrame.capturedScope(magic));
    for (String layout : new String[] {"NTSRSP01", "NTDRSP01", "USRRSP01"})
      assertThrows(
          IllegalArgumentException.class,
          () -> QuestionQueryScopeFrame.wireForInspection(identity(layout, "001"), frame));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionQueryScopeFrame.wireForInspection(identity("QSSRSP01", "002"), frame));
  }

  private static ResponseSnapshotIdentity identity(String layout, String version) {
    return ResponseSnapshotIdentity.authenticated(new UUID(1, 7), layout, version, 7);
  }
}
