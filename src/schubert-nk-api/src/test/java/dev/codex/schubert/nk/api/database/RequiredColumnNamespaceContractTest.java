package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

/** PT-DAT-NAMESPACE001/BUG3198/YKT2664/SS311332/451: no JDBC or authority operation. */
final class RequiredColumnNamespaceContractTest {
  @Test
  void requiredColumnCannotBecomeAnInstanceOrRetainInstanceState() throws Exception {
    assertTrue(Modifier.isFinal(RequiredColumn.class.getModifiers()));
    for (var method : RequiredColumn.class.getDeclaredMethods()) {
      assertTrue(Modifier.isStatic(method.getModifiers()));
    }
    for (var field : RequiredColumn.class.getDeclaredFields()) {
      assertTrue(Modifier.isStatic(field.getModifiers()));
    }
    var constructor = RequiredColumn.class.getDeclaredConstructor();
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
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
