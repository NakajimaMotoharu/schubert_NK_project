package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

/** PT-MED-NAMESPACE001/BUG3198/YKT2664/SS311333/451: no file, network or authority operation. */
final class ContentDispositionNamespaceContractTest {
  @Test
  void contentDispositionCannotBecomeAnInstanceOrRetainInstanceState() throws Exception {
    assertTrue(Modifier.isFinal(ContentDispositionFactory.class.getModifiers()));
    for (var method : ContentDispositionFactory.class.getDeclaredMethods()) {
      assertTrue(Modifier.isStatic(method.getModifiers()));
    }
    for (var field : ContentDispositionFactory.class.getDeclaredFields()) {
      assertTrue(Modifier.isStatic(field.getModifiers()));
    }
    var constructor = ContentDispositionFactory.class.getDeclaredConstructor();
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
