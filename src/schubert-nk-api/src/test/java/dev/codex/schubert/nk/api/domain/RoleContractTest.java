package dev.codex.schubert.nk.api.domain;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-ROLE-CATALOG001; SS314/331/451; vocabulary only, never an authentication or ADMIN grant. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class RoleContractTest {
  @Test
  void roleCatalog001NamesOrderLookupAndValuesIsolationRemainClosed() {
    var expectedNames = List.of("USER", "ADMIN");
    assertEquals(expectedNames, Arrays.stream(Role.values()).map(Enum::name).toList());
    assertEquals(List.of(0, 1), Arrays.stream(Role.values()).map(Enum::ordinal).toList());
    assertSame(Role.USER, Role.valueOf("USER"));
    assertSame(Role.ADMIN, Role.valueOf("ADMIN"));
    var exposed = Role.values();
    exposed[0] = Role.ADMIN;
    assertEquals(expectedNames, Arrays.stream(Role.values()).map(Enum::name).toList());
    for (String unknown : List.of("UNKNOWN", "", "user", "admin", " USER", "ADMIN ")) {
      assertThrows(IllegalArgumentException.class, () -> Role.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> Role.valueOf(null));
  }
}
