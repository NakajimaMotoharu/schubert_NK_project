"""Exact static Main review and all134 NOT_RUN bindings; no dynamic result promotion."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17198-api-observation-static-public-save-v1'
save.BEFORE = '1e1fe098b184cee80eab68f00e7270e91684902e'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17196_', 'tools/quality/pg17198_')
if __name__ == '__main__':
    save.main()
