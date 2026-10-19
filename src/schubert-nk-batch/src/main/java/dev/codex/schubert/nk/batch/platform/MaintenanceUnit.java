package dev.codex.schubert.nk.batch.platform;

import org.jspecify.annotations.NullMarked;

/** Fixed parent stop order, not a command selector. NK-OPS-001/UI251/SS341/343/SSC100/MSTOP001. */
@NullMarked
public enum MaintenanceUnit {
  CADDY("caddy.service"),
  WEB("schubert-nk-web.service"),
  API("schubert-nk-api.service"),
  CLEANUP("schubert-nk-cleanup.service"),
  INSPECTOR("schubert-nk-inbox-inspector.service"),
  EXPIRY("schubert-nk-expiry-cleanup.service"),
  BACKUP("schubert-nk-backup.service"),
  ARTEMIS("artemis.service");

  private final String unitName;

  MaintenanceUnit(String serviceName) {
    this.unitName = serviceName;
  }

  public String serviceName() {
    return unitName;
  }

  public String controlGroup() {
    return "/system.slice/" + unitName;
  }
}
