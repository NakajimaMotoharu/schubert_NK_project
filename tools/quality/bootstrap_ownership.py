"""SSC084/PG289 fixed artifact ownership; package compatibility is not module ownership.

This is a small shared inventory, not an alternate collector or a coverage exclusion.
Unknown bootstrap types fail closed. Historical evidence is never rewritten here.
"""

BOOTSTRAP_MAIN = frozenset("dev.codex.schubert.nk.api." + suffix for suffix in (
    "maintenance.InspectorAesCredential", "maintenance.InspectorDbCredential",
    "maintenance.InspectorCredentialAccess", "file.AesCredentialFile",
    "file.InspectorCredentialException", "file.InspectorCredentialLoader",
    "file.ServiceCredentialException", "file.ServiceCredentialReader",
    "file.ServiceCredentialSet", "bootstrap.ServiceDatabaseAdmission",
    "bootstrap.ServiceDatabaseSource", "file.ServiceProcessResources")) | frozenset((
    "dev.codex.schubert.nk.bootstrap.StartupProofFrame",))
BOOTSTRAP_TEST = frozenset("dev.codex.schubert.nk.api." + suffix for suffix in (
    "maintenance.InspectorAesCredentialTest", "maintenance.InspectorDbCredentialTest",
    "maintenance.InspectorCredentialAccessTest", "file.InspectorCredentialLoaderTest",
    "file.InspectorDatabaseCredentialLoaderTest",
    "file.ServiceCredentialReaderTest", "file.ServiceCredentialSetTest",
    "maintenance.ServiceDatabaseAdmissionTest", "bootstrap.ServiceDatabaseSourceTest",
    "file.ServiceProcessResourcesTest", "logging.ApiLogDatabaseFixture", "maintenance.MaintenanceJdbcProbe")) | frozenset((
    "dev.codex.schubert.nk.bootstrap.StartupProofFrameTest",))


def owner(name, *, test=False):
    canonical = name.replace("/", ".").split("$", 1)[0]
    if canonical in (BOOTSTRAP_TEST if test else BOOTSTRAP_MAIN):
        return "bootstrap"
    for module in ("api", "web", "batch", "storage", "protocol"):
        if canonical.startswith("dev.codex.schubert.nk." + module + "."):
            return module
    raise ValueError("unknown module subject")


def source(repo, name, *, test=False):
    return (repo / ("src/schubert-nk-" + owner(name, test=test))
            / ("src/test/java" if test else "src/main/java")
            / (name.replace(".", "/") + ".java"))
