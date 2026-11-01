"""Exact static fork-agent compatibility scope; no fixture/Product/Source change."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17604-fork-agent-public-save-v1'
save.BEFORE = '1a8add0cad506465e5eb96d77566b6026a0502bf'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17600_', 'tools/quality/pg17604_')
if __name__ == '__main__':
    save.main()
