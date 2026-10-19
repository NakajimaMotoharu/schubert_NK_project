package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.config.ArtemisConnectionFactoryProvider.ConsumerProfile;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDestination;
import java.io.ObjectStreamClass;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG1478/YKT1237; SS314/321/331; PT-F03-ENUM-API001: literal values, no factory or connection. */
final class EnumValueCatalogCompatibilityTest {
  @Test
  void api001FixedProfilesDestinationsAndThresholdsRetainTheirContracts() {
    assertEquals(
        List.of("SYNC", "ASYNC", "WEB_LOG"),
        Arrays.stream(ConsumerProfile.values()).map(Enum::name).toList());
    assertEquals(
        List.of(1_048_576, 0, 65_536),
        Arrays.stream(ConsumerProfile.values()).map(ConsumerProfile::windowBytes).toList());
    assertEquals(
        List.of("ASYNC_WORK", "DLQ"),
        Arrays.stream(OutboxDestination.values()).map(Enum::name).toList());
    assertEquals(
        List.of("nk.async.work", "nk.dead.letter"),
        Arrays.stream(OutboxDestination.values()).map(OutboxDestination::address).toList());
    assertEquals(OutboxDestination.ASYNC_WORK, OutboxDestination.fromAddress("nk.async.work"));
    assertEquals(OutboxDestination.DLQ, OutboxDestination.fromAddress("nk.dead.letter"));
    assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null));
    for (String invalid : List.of("", "nk.sync.request", "NK.ASYNC.WORK")) {
      assertThrows(IllegalArgumentException.class, () -> OutboxDestination.fromAddress(invalid));
    }
    assertEquals(
        List.of("USER", "IP"), Arrays.stream(LoginAttemptKind.values()).map(Enum::name).toList());
    assertEquals(
        List.of(5, 10),
        Arrays.stream(LoginAttemptKind.values()).map(LoginAttemptKind::threshold).toList());
    for (Class<?> type :
        List.of(ConsumerProfile.class, OutboxDestination.class, LoginAttemptKind.class)) {
      var descriptor = ObjectStreamClass.lookup(type);
      assertEquals(0, descriptor.getFields().length, type.getName());
      assertEquals(0L, descriptor.getSerialVersionUID(), type.getName());
    }
  }
}
