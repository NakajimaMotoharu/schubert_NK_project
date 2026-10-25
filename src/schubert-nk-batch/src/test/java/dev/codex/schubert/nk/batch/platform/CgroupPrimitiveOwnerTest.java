package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** OPS009/SYS002004/UI251/SS333343354/SSC308; PT-OPS-CGROUPFD001..008; synthetic FD only. */
final class CgroupPrimitiveOwnerTest {
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
    final FixedUnitCgroupNamespace.Owner owner;
    int next = 319;
    Integer returned;
    Throwable opening;
    Throwable[] closing = new Throwable[0];

    Fixture() {
      DirectoryCalls calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "openRoot", "openDirectory" -> {
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
      owner = new FixedUnitCgroupNamespace.Owner(calls);
    }

    void open(int count) throws StorageIoException {
      int current = owner.openRoot();
      for (int index = 1; index < count; index++)
        current = owner.openDirectory(current, "segment" + index);
    }

    @Override
    public void close() throws StorageIoException {
      owner.close();
    }
  }

  @Test
  void cgroupfd001SixPrimitiveHighDescriptorsKeepOriginalForwardCloseOrder() throws Exception {
    try (var fixture = new Fixture()) {
      fixture.open(6);
      for (int index = 0; index < 6; index++)
        assertEquals(319 + index, fixture.owner.descriptor(index));
      fixture.owner.close();
      fixture.owner.close();
      assertEquals(List.of(319, 320, 321, 322, 323, 324), fixture.closed);
      assertEquals(
          List.of(
              "openRoot",
              "openDirectory",
              "openDirectory",
              "openDirectory",
              "openDirectory",
              "openDirectory"),
          fixture.opened);
    }
  }

  @Test
  void cgroupfd002NullCapacityClosedAndForeignParentFailBeforeNativeIo() throws Exception {
    assertThrows(NullPointerException.class, () -> new FixedUnitCgroupNamespace.Owner(null));
    try (var fixture = new Fixture()) {
      assertThrows(NullPointerException.class, () -> fixture.owner.openDirectory(319, null));
      assertThrows(StorageIoException.class, () -> fixture.owner.openDirectory(319, "foreign"));
      assertTrue(fixture.opened.isEmpty());
      fixture.open(6);
      assertThrows(StorageIoException.class, fixture.owner::openRoot);
      assertThrows(StorageIoException.class, () -> fixture.owner.openDirectory(319, "full"));
      assertEquals(6, fixture.opened.size());
      fixture.owner.close();
      assertThrows(StorageIoException.class, fixture.owner::openRoot);
      assertThrows(StorageIoException.class, () -> fixture.owner.openDirectory(319, "closed"));
      assertEquals(6, fixture.opened.size());
      assertThrows(IndexOutOfBoundsException.class, () -> fixture.owner.descriptor(-1));
      assertThrows(IndexOutOfBoundsException.class, () -> fixture.owner.descriptor(6));
      assertEquals(List.of(319, 320, 321, 322, 323, 324), fixture.closed);
    }
    try (var fixture = new Fixture()) {
      fixture.open(1);
      assertThrows(StorageIoException.class, () -> fixture.owner.openDirectory(999, "foreign"));
      assertEquals(1, fixture.opened.size());
    }
    try (var fixture = new Fixture()) {
      fixture.owner.close();
      fixture.owner.close();
      assertTrue(fixture.closed.isEmpty());
    }
  }

  @Test
  void cgroupfd003NegativeAndDuplicateNeverOwnAnExtraFdButZeroIsValid() throws Exception {
    for (int kind = 0; kind < 2; kind++)
      for (int refused : new int[] {-1, 319, 320}) {
        try (var fixture = new Fixture()) {
          fixture.open(3);
          fixture.returned = refused;
          int selected = kind;
          assertThrows(StorageIoException.class, () -> open(fixture, selected));
          fixture.owner.close();
          assertEquals(List.of(319, 320, 321), fixture.closed);
          assertEquals(4, fixture.opened.size());
        }
      }
    try (var fixture = new Fixture()) {
      fixture.returned = 0;
      assertEquals(0, fixture.owner.openRoot());
      fixture.owner.close();
      assertEquals(List.of(0), fixture.closed);
    }
  }

  @Test
  void cgroupfd004AllOpenFailuresReleaseOnlyPreviouslyOwnedDescriptors() throws Exception {
    for (int kind = 0; kind < 2; kind++)
      for (int type = 1; type < 4; type++) {
        try (var fixture = new Fixture()) {
          fixture.open(1);
          fixture.opening = signal(type);
          int selected = kind;
          Throwable actual =
              assertThrows(
                  Throwable.class,
                  () ->
                      ResourceScope
                          .<FixedUnitCgroupNamespace.Owner, Integer, StorageIoException>acquire(
                              () -> fixture.owner,
                              FixedUnitCgroupNamespace.Owner::close,
                              owner -> open(fixture, selected)));
          if (type == 1)
            fixed(
                assertInstanceOf(StorageIoException.class, actual),
                StorageIoException.Reason.MISSING);
          else assertSame(fixture.opening, actual);
          assertEquals(List.of(319), fixture.closed);
          assertEquals(2, fixture.opened.size());
        }
      }
  }

  @Test
  void cgroupfd005All64ForwardCloseStatesMatchLiteralIndependentGolden() throws Exception {
    for (int first = 0; first < 4; first++)
      for (int middle = 0; middle < 4; middle++)
        for (int last = 0; last < 4; last++) {
          try (var fixture = new Fixture()) {
            fixture.closing = new Throwable[] {signal(first), signal(middle), signal(last)};
            fixture.open(3);
            Throwable actual = null;
            try {
              fixture.owner.close();
            } catch (Throwable observed) {
              actual = observed;
            }
            assertEquals(List.of(319, 320, 321), fixture.closed);
            int column = middle * 4 + last;
            char type = TYPE[first].charAt(column);
            if (type == 'N') assertNull(actual);
            else {
              assertNotNull(actual);
              assertEquals(SUPPRESSED[first].charAt(column) - '0', actual.getSuppressed().length);
              if (type == 'I') {
                int known = (first == 1 ? 1 : 0) + (middle == 1 ? 1 : 0) + (last == 1 ? 1 : 0);
                fixed(
                    assertInstanceOf(StorageIoException.class, actual),
                    known == 1
                        ? StorageIoException.Reason.MISSING
                        : StorageIoException.Reason.UNAVAILABLE);
              } else {
                int winner = WINNER[first].charAt(column) - '0';
                assertSame(fixture.closing[winner], actual);
                assertEquals(
                    type == 'R' ? IllegalStateException.class : AssertionError.class,
                    actual.getClass());
                for (Throwable secondary : actual.getSuppressed())
                  fixed(
                      assertInstanceOf(StorageIoException.class, secondary),
                      StorageIoException.Reason.UNAVAILABLE);
              }
            }
          }
        }
  }

  @Test
  void cgroupfd006ExistingAndRepeatedSuppressionKeepIdentityAndSanitizeLaterFailures()
      throws Exception {
    try (var fixture = new Fixture()) {
      var primary = new StorageIoException(StorageIoException.Reason.MISSING);
      primary.addSuppressed(new IOException("PUBLIC_PRIOR"));
      fixture.closing = new Throwable[] {primary, null, null};
      fixture.open(3);
      fixed(
          assertThrows(StorageIoException.class, fixture.owner::close),
          StorageIoException.Reason.UNAVAILABLE);
      assertEquals(List.of(319, 320, 321), fixture.closed);
    }
    try (var fixture = new Fixture()) {
      var primary = new IllegalStateException("PUBLIC_UNKNOWN");
      var prior = new IOException("PUBLIC_PRIOR");
      primary.addSuppressed(prior);
      fixture.closing = new Throwable[] {primary, primary, signal(1)};
      fixture.open(3);
      assertSame(primary, assertThrows(IllegalStateException.class, fixture.owner::close));
      assertEquals(3, primary.getSuppressed().length);
      assertSame(prior, primary.getSuppressed()[0]);
      for (int index = 1; index < 3; index++)
        fixed(
            assertInstanceOf(StorageIoException.class, primary.getSuppressed()[index]),
            StorageIoException.Reason.UNAVAILABLE);
      assertEquals(List.of(319, 320, 321), fixture.closed);
    }
  }

  @Test
  void cgroupfd007SixSlotsDrainEveryLaterFdBeforeUnknownAggregationAndNeverRetry()
      throws Exception {
    try (var fixture = new Fixture()) {
      Throwable unknown = signal(2);
      fixture.closing = new Throwable[] {signal(1), unknown, signal(1), signal(3), null, signal(1)};
      fixture.open(6);
      assertSame(unknown, assertThrows(IllegalStateException.class, fixture.owner::close));
      assertNotNull(unknown);
      assertEquals(3, unknown.getSuppressed().length);
      for (Throwable secondary : unknown.getSuppressed())
        fixed(
            assertInstanceOf(StorageIoException.class, secondary),
            StorageIoException.Reason.UNAVAILABLE);
      assertEquals(List.of(319, 320, 321, 322, 323, 324), fixture.closed);
      fixture.owner.close();
      assertEquals(6, fixture.closed.size());
      assertThrows(StorageIoException.class, fixture.owner::openRoot);
      assertEquals(6, fixture.opened.size());
    }
  }

  @Test
  void cgroupfd008ParallelOwnersNeverShareSlotsOrConsumeEachOther() throws Exception {
    var ready = new CountDownLatch(2);
    try (var first = new Fixture();
        var second = new Fixture();
        var executor = Executors.newFixedThreadPool(2)) {
      var a = executor.submit(() -> parallel(first, ready));
      var b = executor.submit(() -> parallel(second, ready));
      assertEquals(List.of(319, 320, 321), a.get());
      assertEquals(List.of(319, 320, 321), b.get());
      assertNotSame(first.owner, second.owner);
    }
  }

  private static List<Integer> parallel(Fixture fixture, CountDownLatch ready) throws Exception {
    fixture.open(3);
    ready.countDown();
    assertTrue(ready.await(10, TimeUnit.SECONDS));
    fixture.owner.close();
    return List.copyOf(fixture.closed);
  }

  private static int open(Fixture fixture, int kind) throws StorageIoException {
    return kind == 0 ? fixture.owner.openRoot() : fixture.owner.openDirectory(319, "next");
  }

  private static Throwable signal(int kind) {
    return switch (kind) {
      case 0 -> null;
      case 1 -> new StorageIoException(StorageIoException.Reason.MISSING);
      case 2 -> new IllegalStateException("PUBLIC_UNKNOWN");
      default -> new AssertionError("PUBLIC_UNKNOWN");
    };
  }

  private static void fixed(StorageIoException failure, StorageIoException.Reason reason) {
    assertEquals(reason, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
