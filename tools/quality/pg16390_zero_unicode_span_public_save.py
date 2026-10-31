"""Exact public span-tool qualification delta; no security HOLD release or Product execution."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16390-zero-unicode-span-public-save-v1'
save.BEFORE='3fa926f52c11fec148f09fc83392ce0eefec462b'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16386_',
    'tools/quality/pg16388_','tools/quality/pg16390_',
    'tools/quality/pmd_source_span_no_unicode_translation.py')

if __name__=='__main__':save.main()
