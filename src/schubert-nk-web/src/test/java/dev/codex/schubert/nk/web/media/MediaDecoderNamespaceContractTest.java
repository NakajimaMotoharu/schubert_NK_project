package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import org.junit.jupiter.api.Test;

/** PT-MED-NAMESPACE001/BUG3206/YKT2664/SS333/451: pure projection codec only. */
final class MediaDecoderNamespaceContractTest {
  @Test
  void mediaDecoderCannotBecomeAnInstanceOrRetainInstanceState() throws Exception {
    assertTrue(Modifier.isFinal(MediaResponseDecoder.class.getModifiers()));
    for (var method : MediaResponseDecoder.class.getDeclaredMethods()) {
      assertTrue(Modifier.isStatic(method.getModifiers()));
    }
    for (var field : MediaResponseDecoder.class.getDeclaredFields()) {
      assertTrue(Modifier.isStatic(field.getModifiers()));
    }
    var constructor = MediaResponseDecoder.class.getDeclaredConstructor();
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
