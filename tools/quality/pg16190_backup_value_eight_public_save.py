"""Exact public synthetic metadata/ordinary PT and periodic review delta; no live resource access."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16190-backup-value-eight-public-save-v1'
runner.BEFORE='a8d2b9183d4019bad6026ebbdc7319571242c2c4'
runner.PREFIXES+=('tools/quality/pg16176_','tools/quality/pg16178_','tools/quality/pg16180_','tools/quality/pg16182_',
    'tools/quality/pg16184_','tools/quality/pg16186_','tools/quality/pg16188_','tools/quality/pg16190_',
    'tools/quality/architecture/MorningBackupValueEightJunitLauncher.java')

if __name__=='__main__':
    runner.main()
