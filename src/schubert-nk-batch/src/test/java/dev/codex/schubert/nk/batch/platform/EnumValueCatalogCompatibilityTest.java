package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.ObjectStreamClass;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG1478/YKT1237; SS341/343; PT-F03-ENUM-OPS001: enum values only, never starts/stops Units. */
final class EnumValueCatalogCompatibilityTest {
  private static final String API_NAME = "API";
  private static final String WEB_NAME = "WEB";
  private static final String API_UNIT_NAME = "schubert-nk-api.service";
  private static final String WEB_UNIT_NAME = "schubert-nk-web.service";
  private static final String CLEANUP_NAME = "CLEANUP";
  private static final String INSPECTOR_NAME = "INSPECTOR";
  private static final String EXPIRY_NAME = "EXPIRY";
  private static final String BACKUP_NAME = "BACKUP";
  private static final String ARTEMIS_NAME = "ARTEMIS";

  @Test
  void ops001UnitAndStartTargetCatalogsKeepTheirApprovedLiterals() {
    assertEquals(
        List.of(API_NAME, WEB_NAME),
        Arrays.stream(ApplicationUnit.values()).map(Enum::name).toList());
    assertEquals(
        List.of(API_UNIT_NAME, WEB_UNIT_NAME),
        Arrays.stream(ApplicationUnit.values()).map(ApplicationUnit::serviceName).toList());
    assertEquals(
        List.of(
            "CADDY",
            WEB_NAME,
            API_NAME,
            CLEANUP_NAME,
            INSPECTOR_NAME,
            EXPIRY_NAME,
            BACKUP_NAME,
            ARTEMIS_NAME),
        Arrays.stream(MaintenanceUnit.values()).map(Enum::name).toList());
    var maintenanceUnits =
        List.of(
            "caddy.service",
            WEB_UNIT_NAME,
            API_UNIT_NAME,
            "schubert-nk-cleanup.service",
            "schubert-nk-inbox-inspector.service",
            "schubert-nk-expiry-cleanup.service",
            "schubert-nk-backup.service",
            "artemis.service");
    assertEquals(
        maintenanceUnits,
        Arrays.stream(MaintenanceUnit.values()).map(MaintenanceUnit::serviceName).toList());
    assertEquals(
        maintenanceUnits.stream().map(name -> "/system.slice/" + name).toList(),
        Arrays.stream(MaintenanceUnit.values()).map(MaintenanceUnit::controlGroup).toList());
    assertEquals(
        List.of(API_NAME, WEB_NAME, "MORNING", CLEANUP_NAME, EXPIRY_NAME),
        Arrays.stream(RootStartupContext.Service.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            API_UNIT_NAME,
            WEB_UNIT_NAME,
            "schubert-nk-morning-controller.service",
            "schubert-nk-cleanup.service",
            "schubert-nk-expiry-cleanup.service"),
        Arrays.stream(RootStartupContext.Service.values())
            .map(RootStartupContext.Service::unit)
            .toList());
    assertEquals(
        List.of(
            INSPECTOR_NAME,
            BACKUP_NAME,
            CLEANUP_NAME,
            EXPIRY_NAME,
            ARTEMIS_NAME,
            "MORNING",
            API_NAME,
            WEB_NAME),
        Arrays.stream(InspectorUnitSnapshot.Target.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            "schubert-nk-inbox-inspector.service",
            "schubert-nk-backup.service",
            "schubert-nk-cleanup.service",
            "schubert-nk-expiry-cleanup.service",
            "artemis.service",
            "schubert-nk-morning-controller.service",
            API_UNIT_NAME,
            WEB_UNIT_NAME),
        Arrays.stream(InspectorUnitSnapshot.Target.values())
            .map(InspectorUnitSnapshot.Target::unit)
            .toList());
    assertEquals(
        List.of(BACKUP_NAME, CLEANUP_NAME, INSPECTOR_NAME, EXPIRY_NAME, "BROKER"),
        Arrays.stream(BackupUnitStartClient.Target.values()).map(Enum::name).toList());
    assertEquals(
        List.of(BACKUP_NAME, CLEANUP_NAME, INSPECTOR_NAME, EXPIRY_NAME, ARTEMIS_NAME),
        Arrays.stream(BackupUnitStartClient.Target.values())
            .map(value -> value.unit().name())
            .toList());
    assertEquals(
        List.of(BACKUP_NAME, CLEANUP_NAME, INSPECTOR_NAME, EXPIRY_NAME, ARTEMIS_NAME),
        Arrays.stream(BackupUnitStartClient.Target.values())
            .map(value -> value.observation().name())
            .toList());
    assertEquals(
        List.of(
            "/run/schubert-nk/backup-request",
            "/run/schubert-nk/cleanup-request",
            "/run/schubert-nk/cleanup-request",
            "/run/schubert-nk/expiry-request",
            "/run/schubert-nk/startup"),
        Arrays.stream(BackupUnitStartClient.Target.values())
            .map(BackupUnitStartClient.Target::requestDirectory)
            .toList());
    assertEquals(
        List.of(
            "backup-start.intent",
            "cleanup-start.intent",
            "inspector-start.intent",
            "expiry-start.intent",
            "broker-start.intent"),
        Arrays.stream(BackupUnitStartClient.Target.values())
            .map(BackupUnitStartClient.Target::marker)
            .toList());
    for (var target : BackupUnitStartClient.Target.values()) {
      assertEquals(false, target.ownedBy(null));
      for (var service : RootStartupContext.Service.values()) {
        assertEquals(
            target == BackupUnitStartClient.Target.INSPECTOR
                ? service == RootStartupContext.Service.CLEANUP
                : service == RootStartupContext.Service.MORNING,
            target.ownedBy(service));
      }
    }
    for (Class<?> type :
        List.of(
            ApplicationUnit.class,
            MaintenanceUnit.class,
            RootStartupContext.Service.class,
            InspectorUnitSnapshot.Target.class,
            BackupUnitStartClient.Target.class)) {
      var descriptor = ObjectStreamClass.lookup(type);
      assertEquals(0, descriptor.getFields().length, type.getName());
      assertEquals(0L, descriptor.getSerialVersionUID(), type.getName());
    }
  }
}
