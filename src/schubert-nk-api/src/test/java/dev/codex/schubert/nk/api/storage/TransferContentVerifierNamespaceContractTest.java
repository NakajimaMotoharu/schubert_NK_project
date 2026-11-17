package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

/** PT-SCN-008-W06-NAMESPACE, BUG-3209, YKT-2664, SS333. */
final class TransferContentVerifierNamespaceContractTest {
  @Test
  void staticNamespaceCannotBeInstantiated() throws Exception {
    var type = TransferContentVerifier.class;
    var constructor = type.getDeclaredConstructor();
    assertTrue(Modifier.isFinal(type.getModifiers()));
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
    for (var field : type.getDeclaredFields()) {
      assertTrue(Modifier.isStatic(field.getModifiers()));
    }
    for (var method : type.getDeclaredMethods()) {
      assertTrue(Modifier.isStatic(method.getModifiers()));
    }
    boolean before = constructor.canAccess(null);
    assertFalse(before);
    try {
      assertTrue(constructor.trySetAccessible());
      var failure = assertThrows(InvocationTargetException.class, constructor::newInstance);
      assertEquals(AssertionError.class, failure.getCause().getClass());
      assertEquals("static namespace", failure.getCause().getMessage());
      assertNull(failure.getCause().getCause());
      assertEquals(0, failure.getCause().getSuppressed().length);
    } finally {
      constructor.setAccessible(before);
    }
    assertFalse(constructor.canAccess(null));
  }
}
