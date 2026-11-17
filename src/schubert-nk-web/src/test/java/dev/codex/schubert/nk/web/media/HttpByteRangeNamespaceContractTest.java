package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.InvocationTargetException;
import org.junit.jupiter.api.Test;

/** PT-MED-NAMESPACE001; SS333354/PG-D1175; one internal pure class, no native or access path. */
final class HttpByteRangeNamespaceContractTest {
  @Test
  void namespace001StaticUtilityRejectsConstructionAndRestoresAccess() throws Exception {
    var constructor = HttpByteRangeParser.class.getDeclaredConstructor();
    boolean originalAccess = constructor.canAccess(null);
    assertFalse(originalAccess);
    try {
      constructor.setAccessible(true);
      var wrapped = assertThrows(InvocationTargetException.class, constructor::newInstance);
      var failure = assertInstanceOf(AssertionError.class, wrapped.getCause());
      assertEquals("static utility", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    } finally {
      constructor.setAccessible(originalAccess);
    }
    assertEquals(originalAccess, constructor.canAccess(null));
    assertThrows(IllegalAccessException.class, constructor::newInstance);
  }
}
