package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/SYS002004/UI251/SS333343354/SSC308; PT-OPS-VIEWFD001..008. */
final class StartupAdmissionViewOwnerTest {
  private static final String FIXTURE_PRIMARY_9466F7E5 = "PRIMARY";
  private static final String[] TYPE = {
    "NIREIIRERRRREEEE", "IIREIIRERRRREEEE", "RRRRRRRRRRRRRRRR", "EEEEEEEEEEEEEEEE"
  };
  private static final String[] SUPPRESSED = {
    "0000000001110111", "0000000001110111", "0111122212221222", "0111122212221222"
  };
  private static final String[] WINNER = {
    "xx22xx2211111111", "xx22xx2211111111", "0000000000000000", "0000000000000000"
  };

  private static final class Fixture implements AutoCloseable {
    final List<Integer> closed = new ArrayList<>();
    final List<String> opened = new ArrayList<>();
    final DirectoryCalls calls;
    final StartupAdmissionFile.ViewOwner owner;
    int next = 319;
    Integer returned;
    Throwable opening;
    Throwable[] closing = new Throwable[0];

    Fixture(int capacity) {
      calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "openRoot", "openDirectory", "openEntry" -> {
                        opened.add(method.getName());
                        if (opening != null) throw opening;
                        int value = returned == null ? next++ : returned;
                        returned = null;
                        return value;
                      }
                      case "close" -> {
                        closed.add((Integer) args[0]);
                        int index = closed.size() - 1;
                        if (index < closing.length && closing[index] != null) throw closing[index];
                        return null;
                      }
                      default -> throw new AssertionError("no other native capability");
                    }
                  });
      owner = new StartupAdmissionFile.ViewOwner(calls, capacity);
    }

    @Override
    public void close() throws StorageIoException {
      owner.close();
    }
  }

  private static void three(Fixture fixture) throws StorageIoException {
    assertEquals(319, fixture.owner.openRoot());
    assertEquals(320, fixture.owner.openDirectory(319, "schubert-nk"));
    assertEquals(321, fixture.owner.openEntry(320, "startup-admission.lock"));
  }

  private static int open(Fixture fixture, int kind) throws StorageIoException {
    return switch (kind) {
      case 0 -> fixture.owner.openRoot();
      case 1 -> fixture.owner.openDirectory(319, "child");
      case 2 -> fixture.owner.openEntry(319, "entry");
      default -> throw new AssertionError("literal native open kind");
    };
  }

  private static Throwable signal(int type) {
    return switch (type) {
      case 0 -> null;
      case 1 -> new StorageIoException(StorageIoException.Reason.MISSING);
      case 2 -> new IllegalStateException("synthetic runtime");
      case 3 -> new AssertionError("synthetic error, not heap exhaustion");
      default -> throw new AssertionError("literal four states");
    };
  }

  private static Boolean failBody(Throwable failure) throws IOException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  @Test
  void viewfd001PrimitiveHighDescriptorsCloseInReverseExactlyOnce() throws Exception {
    try (var fixture = new Fixture(3)) {
      three(fixture);
      assertEquals(List.of("openRoot", "openDirectory", "openEntry"), fixture.opened);
      assertTrue(fixture.closed.isEmpty());
      fixture.owner.close();
      fixture.owner.close();
      assertEquals(List.of(321, 320, 319), fixture.closed);
    }
  }

  @Test
  void viewfd002CapacityClosedNullAndParentRefuseBeforeNativeOpen() throws Exception {
    assertThrows(NullPointerException.class, () -> new StartupAdmissionFile.ViewOwner(null, 1));
    try (var fixture = new Fixture(3)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupAdmissionFile.ViewOwner(fixture.calls, 0));
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupAdmissionFile.ViewOwner(fixture.calls, -1));
      assertThrows(NullPointerException.class, () -> fixture.owner.openDirectory(319, null));
      assertThrows(NullPointerException.class, () -> fixture.owner.openEntry(319, null));
      assertThrows(
          StorageIoException.class, () -> fixture.owner.openDirectory(319, "missing parent"));
      assertThrows(StorageIoException.class, () -> fixture.owner.openEntry(319, "missing parent"));
      assertTrue(fixture.opened.isEmpty());
      three(fixture);
      for (int kind = 0; kind < 3; kind++) {
        int selected = kind;
        assertThrows(StorageIoException.class, () -> open(fixture, selected));
      }
      assertEquals(3, fixture.opened.size());
      fixture.owner.close();
      for (int kind = 0; kind < 3; kind++) {
        int selected = kind;
        assertThrows(StorageIoException.class, () -> open(fixture, selected));
      }
      assertEquals(3, fixture.opened.size());
      assertEquals(List.of(321, 320, 319), fixture.closed);
    }
    try (var fixture = new Fixture(3)) {
      assertEquals(319, fixture.owner.openRoot());
      assertThrows(StorageIoException.class, () -> fixture.owner.openDirectory(999, "foreign"));
      assertThrows(StorageIoException.class, () -> fixture.owner.openEntry(999, "foreign"));
      assertEquals(1, fixture.opened.size());
    }
  }

  @Test
  void viewfd003NegativeAndDuplicateNeverCreateAnExtraOwnershipSlot() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      for (int refused : new int[] {-1, 319, 320}) {
        try (var fixture = new Fixture(4)) {
          assertEquals(319, fixture.owner.openRoot());
          assertEquals(320, fixture.owner.openRoot());
          fixture.returned = refused;
          int selected = kind;
          assertThrows(StorageIoException.class, () -> open(fixture, selected));
          fixture.owner.close();
          assertEquals(List.of(320, 319), fixture.closed);
        }
      }
    }
    for (int kind = 0; kind < 3; kind++) {
      try (var fixture = new Fixture(3)) {
        assertEquals(319, fixture.owner.openRoot());
        assertEquals(320, open(fixture, kind));
        fixture.owner.close();
        assertEquals(List.of(320, 319), fixture.closed);
      }
    }
    try (var fixture = new Fixture(1)) {
      fixture.returned = 0;
      assertEquals(0, fixture.owner.openRoot());
      fixture.owner.close();
      assertEquals(List.of(0), fixture.closed);
    }
  }

  @Test
  void viewfd004AllNativeOpenFailureKindsRetainOnlyPriorOwnedDescriptors() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      for (int type = 1; type < 4; type++) {
        try (var fixture = new Fixture(3)) {
          assertEquals(319, fixture.owner.openRoot());
          fixture.opening = signal(type);
          int selected = kind;
          var actual =
              assertThrows(
                  Throwable.class,
                  () ->
                      ResourceScope
                          .<StartupAdmissionFile.ViewOwner, Integer, StorageIoException>acquire(
                              () -> fixture.owner,
                              StartupAdmissionFile.ViewOwner::close,
                              owner -> open(fixture, selected)));
          if (type == 1) {
            assertInstanceOf(StorageIoException.class, actual);
            assertEquals(StorageIoException.Reason.MISSING, ((StorageIoException) actual).reason());
            assertEquals(0, actual.getSuppressed().length);
          } else assertSame(fixture.opening, actual);
          assertEquals(List.of(319), fixture.closed);
          assertEquals(2, fixture.opened.size());
        }
      }
    }
  }

  @Test
  void viewfd005All64ReverseCloseStatesMatchFixedIndependentGolden() throws Exception {
    for (int first = 0; first < 4; first++) {
      for (int middle = 0; middle < 4; middle++) {
        for (int last = 0; last < 4; last++) {
          try (var fixture = new Fixture(3)) {
            fixture.closing = new Throwable[] {signal(first), signal(middle), signal(last)};
            three(fixture);
            Throwable actual = null;
            try {
              fixture.owner.close();
            } catch (Throwable observed) {
              actual = observed;
            }
            int column = middle * 4 + last;
            char type = TYPE[first].charAt(column);
            assertEquals(List.of(321, 320, 319), fixture.closed);
            if (type == 'N') assertNull(actual);
            else {
              assertNotNull(actual);
              assertEquals(SUPPRESSED[first].charAt(column) - '0', actual.getSuppressed().length);
              if (type == 'I') {
                assertInstanceOf(StorageIoException.class, actual);
                int ioCount = (first == 1 ? 1 : 0) + (middle == 1 ? 1 : 0) + (last == 1 ? 1 : 0);
                assertEquals(
                    ioCount == 1
                        ? StorageIoException.Reason.MISSING
                        : StorageIoException.Reason.UNAVAILABLE,
                    ((StorageIoException) actual).reason());
              } else {
                if (type == 'R') assertInstanceOf(IllegalStateException.class, actual);
                else assertInstanceOf(AssertionError.class, actual);
                assertSame(fixture.closing[WINNER[first].charAt(column) - '0'], actual);
                for (var suppressed : actual.getSuppressed()) {
                  assertInstanceOf(StorageIoException.class, suppressed);
                  assertEquals(
                      StorageIoException.Reason.UNAVAILABLE,
                      ((StorageIoException) suppressed).reason());
                }
              }
            }
            assertDoesNotThrow(fixture.owner::close);
            assertEquals(3, fixture.closed.size());
          }
        }
      }
    }
  }

  @Test
  void viewfd006ExistingSuppressedAndRepeatedThrowableStaySanitized() throws Exception {
    try (var fixture = new Fixture(3)) {
      var known = new StorageIoException(StorageIoException.Reason.MISSING);
      known.addSuppressed(new AssertionError("synthetic old detail"));
      fixture.closing = new Throwable[] {known};
      three(fixture);
      var actual = assertThrows(StorageIoException.class, fixture.owner::close);
      assertEquals(StorageIoException.Reason.UNAVAILABLE, actual.reason());
      assertEquals(0, actual.getSuppressed().length);
      assertNotSame(known, actual);
      assertEquals(List.of(321, 320, 319), fixture.closed);
    }
    try (var fixture = new Fixture(3)) {
      var shared = new IllegalStateException("synthetic same instance");
      shared.addSuppressed(new IllegalArgumentException("synthetic existing"));
      fixture.closing = new Throwable[] {shared, shared, shared};
      three(fixture);
      assertSame(shared, assertThrows(IllegalStateException.class, fixture.owner::close));
      assertEquals(3, shared.getSuppressed().length);
      assertInstanceOf(StorageIoException.class, shared.getSuppressed()[1]);
      assertInstanceOf(StorageIoException.class, shared.getSuppressed()[2]);
      assertEquals(List.of(321, 320, 319), fixture.closed);
    }
  }

  @Test
  void viewfd007BodyAndOwnerCloseKeepExistingIndependentPriority() throws Exception {
    String[][] expected = {
      {"IO", "CLOSE", "CLOSE"},
      {FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5},
      {FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5, FIXTURE_PRIMARY_9466F7E5}
    };
    for (int body = 0; body < 3; body++) {
      for (int close = 0; close < 3; close++) {
        try (var fixture = new Fixture(3)) {
          Throwable[] primary = {
            new IOException("synthetic body IO"),
            new IllegalStateException("synthetic body runtime"),
            new AssertionError("synthetic body error")
          };
          Throwable before = primary[body];
          Throwable secondary = signal(close + 1);
          fixture.closing = new Throwable[] {secondary};
          var actual =
              assertThrows(
                  Throwable.class,
                  () ->
                      ResourceScope
                          .<StartupAdmissionFile.ViewOwner, Boolean, StorageIoException>acquire(
                              () -> fixture.owner,
                              StartupAdmissionFile.ViewOwner::close,
                              owner -> {
                                three(fixture);
                                return failBody(before);
                              }));
          switch (expected[body][close]) {
            case "IO" -> {
              assertInstanceOf(StorageIoException.class, actual);
              assertEquals(
                  StorageIoException.Reason.UNAVAILABLE, ((StorageIoException) actual).reason());
              assertNotSame(before, actual);
              assertNotSame(secondary, actual);
            }
            case "CLOSE" -> assertSame(secondary, actual);
            case FIXTURE_PRIMARY_9466F7E5 -> {
              assertSame(before, actual);
              assertEquals(1, actual.getSuppressed().length);
              assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
              assertNotSame(secondary, actual.getSuppressed()[0]);
            }
            default -> fail("literal priority table");
          }
          assertEquals(List.of(321, 320, 319), fixture.closed);
        }
      }
    }
  }

  @Test
  void viewfd008IndependentParallelOwnersNeverShareSlotsOrConsumeEachOther() throws Exception {
    Callable<List<Integer>> operation =
        () -> {
          try (var fixture = new Fixture(3)) {
            three(fixture);
            fixture.owner.close();
            return List.copyOf(fixture.closed);
          }
        };
    try (var executor = Executors.newFixedThreadPool(2)) {
      var first = executor.submit(operation);
      var second = executor.submit(operation);
      assertEquals(List.of(321, 320, 319), first.get());
      assertEquals(List.of(321, 320, 319), second.get());
    }
  }
}
