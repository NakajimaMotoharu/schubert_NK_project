"""Exact Scenario audit original5/current2655 evidence; preserve failed NoCode fixture version."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17286-scenario-audit-public-save-v1'
save.BEFORE = '85e23d810487ac99c79e8fc3b7f1e705a60cd833'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17270_', 'tools/quality/pg17272_', 'tools/quality/pg17274_', 'tools/quality/pg17275_', 'tools/quality/pg17276_', 'tools/quality/pg17278_', 'tools/quality/pg17280_', 'tools/quality/pg17282_', 'tools/quality/pg17284_', 'tools/quality/pg17286_', 'tools/quality/architecture/ScenarioAuditFiveCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
