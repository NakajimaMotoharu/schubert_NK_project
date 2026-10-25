package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/**
 * PT-DB-INBOX-113..120; hand-built Linux UAPI golden, no actual credential or production oracle.
 */
final class InspectorCredentialAccessTest {
  private static final long UID = 1000;
  private final InspectorCredentialAccess policy = new InspectorCredentialAccess(UID);

  @Test
  void rootAclFileAndDirectory() {
    for (long uid : new long[] {1, UID, 0xffff_fffeL}) {
      var access = new InspectorCredentialAccess(uid);
      for (boolean readonly : new boolean[] {false, true}) {
        for (long size : new long[] {54, 55, 69})
          assertDoesNotThrow(
              () -> access.requireAesFile(0100440, 0, 1, size, readonly, golden(uid, false)));
        for (int links : new int[] {1, 2, Integer.MAX_VALUE})
          assertDoesNotThrow(
              () -> access.requireDirectory(040550, 0, links, readonly, golden(uid, true)));
      }
    }
  }

  @Test
  void ownedReadonlyFallback() {
    for (long uid : new long[] {1, UID, 0xffff_fffeL}) {
      var access = new InspectorCredentialAccess(uid);
      assertDoesNotThrow(() -> access.requireAesFile(0100400, uid, 1, 54, true, new byte[0]));
      assertDoesNotThrow(() -> access.requireDirectory(040500, uid, 1, true, new byte[0]));
      invalid(() -> access.requireAesFile(0100400, uid, 1, 54, false, new byte[0]));
      invalid(() -> access.requireDirectory(040500, uid, 1, false, new byte[0]));
      invalid(() -> access.requireAesFile(0100400, uid, 1, 54, true, golden(uid, false)));
      invalid(() -> access.requireDirectory(040500, uid, 1, true, golden(uid, true)));
      invalid(() -> access.requireAesFile(0100400, 0, 1, 54, true, new byte[0]));
      invalid(() -> access.requireDirectory(040500, 0, 1, true, new byte[0]));
    }
  }

  @Test
  void inodeTypeAndMode() {
    for (int bit = 0; bit < 32; bit++) {
      int difference = 1 << bit;
      invalid(
          () -> policy.requireAesFile(0100440 ^ difference, 0, 1, 54, true, golden(UID, false)));
      invalid(() -> policy.requireDirectory(040550 ^ difference, 0, 1, true, golden(UID, true)));
      invalid(() -> policy.requireAesFile(0100400 ^ difference, UID, 1, 54, true, new byte[0]));
      invalid(() -> policy.requireDirectory(040500 ^ difference, UID, 1, true, new byte[0]));
    }
    for (int type : new int[] {0, 010000, 020000, 040000, 060000, 0120000, 0140000})
      invalid(() -> policy.requireAesFile(type | 0440, 0, 1, 54, true, golden(UID, false)));
    for (int type : new int[] {0, 010000, 020000, 060000, 0100000, 0120000, 0140000})
      invalid(() -> policy.requireDirectory(type | 0550, 0, 1, true, golden(UID, true)));
  }

  @Test
  void linkSizeAndUidBounds() {
    for (long uid : new long[] {Long.MIN_VALUE, -1, 0, 0xffff_ffffL, Long.MAX_VALUE})
      invalid(() -> new InspectorCredentialAccess(uid));
    for (long owner : new long[] {-1, 1, 1001, 0xffff_ffffL, Long.MAX_VALUE}) {
      invalid(() -> policy.requireAesFile(0100400, owner, 1, 54, true, new byte[0]));
      invalid(() -> policy.requireDirectory(040500, owner, 1, true, new byte[0]));
    }
    for (int links : new int[] {Integer.MIN_VALUE, -1, 0, 2, Integer.MAX_VALUE})
      invalid(() -> policy.requireAesFile(0100440, 0, links, 54, true, golden(UID, false)));
    for (int links : new int[] {Integer.MIN_VALUE, -1, 0})
      invalid(() -> policy.requireDirectory(040550, 0, links, true, golden(UID, true)));
    for (long size : new long[] {Long.MIN_VALUE, -1, 0, 53, 70, Long.MAX_VALUE})
      invalid(() -> policy.requireAesFile(0100440, 0, 1, size, true, golden(UID, false)));
  }

  @Test
  void everyAclBitAndShape() {
    for (boolean directory : new boolean[] {false, true}) {
      byte[] original = golden(UID, directory);
      for (int bit = 0; bit < original.length * 8; bit++) {
        byte[] changed = original.clone();
        changed[bit / 8] ^= (byte) (1 << (bit % 8));
        invalid(() -> check(directory, changed));
      }
      for (int length : new int[] {0, 1, 4, 28, 36, 43, 45, 52, 1000})
        invalid(() -> check(directory, Arrays.copyOf(original, length)));
      byte[] extraUser = Arrays.copyOf(original, 52);
      System.arraycopy(original, 12, extraUser, 44, 8);
      extraUser[46] = 0; // Additional named entry denied even with no permission.
      extraUser[48]++;
      invalid(() -> check(directory, extraUser));
      extraUser[44] = 8; // Named group is also forbidden.
      invalid(() -> check(directory, extraUser));
      byte[] swapped = original.clone();
      System.arraycopy(original, 4, swapped, 12, 8);
      System.arraycopy(original, 12, swapped, 4, 8);
      invalid(() -> check(directory, swapped));
    }
  }

  @Test
  void nullAndInputOwnership() {
    assertThrows(
        NullPointerException.class, () -> policy.requireAesFile(0100440, 0, 1, 54, true, null));
    assertThrows(
        NullPointerException.class, () -> policy.requireDirectory(040550, 0, 1, true, null));
    assertThrows(
        NullPointerException.class, () -> policy.requireAesFile(0100400, UID, 1, 54, true, null));
    assertThrows(
        NullPointerException.class, () -> policy.requireDirectory(040500, UID, 1, true, null));
    for (boolean directory : new boolean[] {false, true}) {
      byte[] acl = golden(UID, directory);
      byte[] before = acl.clone();
      check(directory, acl);
      assertArrayEquals(before, acl);
      Arrays.fill(acl, (byte) 0);
      invalid(() -> check(directory, acl));
      assertDoesNotThrow(() -> check(directory, before)); // no mutable input retained
      invalid(() -> check(directory, new byte[44]));
    }
  }

  @Test
  void concurrentPoliciesDoNotCross() throws Exception {
    try (var pool = Executors.newFixedThreadPool(12)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 1; i <= 100; i++) {
        long uid = i;
        tasks.add(
            () -> {
              var access = new InspectorCredentialAccess(uid);
              access.requireAesFile(0100440, 0, 1, 69, false, golden(uid, false));
              access.requireDirectory(040550, 0, 2, false, golden(uid, true));
              access.requireAesFile(0100400, uid, 1, 54, true, new byte[0]);
              invalid(() -> access.requireDirectory(040550, 0, 1, true, golden(uid + 1, true)));
              check(false, golden(UID, false)); // shared policy remains immutable
              return true;
            });
      }
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void errorsAreFixedAndNonMutating() {
    byte[] wrong = golden(1001, false);
    byte[] before = wrong.clone();
    invalid(() -> policy.requireAesFile(0100440, 0, 1, 54, true, wrong));
    assertArrayEquals(before, wrong);
    invalid(() -> policy.requireDirectory(040550, 0, 1, true, wrong));
    assertArrayEquals(before, wrong);
    // A mask in st_mode does not authorize GROUP_OBJ or OTHER permissions.
    for (int position : new int[] {22, 38}) {
      byte[] leaked = golden(UID, false);
      leaked[position] = 4;
      invalid(() -> check(false, leaked));
    }
    assertDoesNotThrow(() -> check(false, golden(UID, false)));
  }

  private void check(boolean directory, byte[] acl) {
    if (directory) policy.requireDirectory(040550, 0, 2, false, acl);
    else policy.requireAesFile(0100440, 0, 1, 54, false, acl);
  }

  private static byte[] golden(long uid, boolean directory) {
    // Public metadata: version2 and five entries; USER id occupies offsets16..19.
    byte[] bytes =
        HexFormat.of()
            .parseHex(
                "0200000001000400ffffffff020004000000000004000000ffffffff10000400ffffffff20000000ffffffff");
    for (int index = 0; index < 4; index++) bytes[16 + index] = (byte) (uid >>> (8 * index));
    if (directory) for (int index : new int[] {6, 14, 30}) bytes[index] = 5;
    return bytes;
  }

  private static void invalid(Executable action) {
    var error = assertThrows(IllegalArgumentException.class, action);
    assertEquals("inspector credential access is invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
