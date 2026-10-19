package dev.codex.schubert.nk.batch.platform;

/** NK-OPS-001; OPS-009; UI251; SS341/343; PG-D-148; PT-OPS-STOP-001/008/009. */
enum ApplicationUnit {
  API("schubert-nk-api.service"),
  WEB("schubert-nk-web.service");
  private final String unitName;

  ApplicationUnit(String serviceName) {
    this.unitName = serviceName;
  }

  String serviceName() {
    return unitName;
  }
}
