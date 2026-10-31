"""Exact changed public text only; held paths excluded before metadata/content access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16056-backup-request-public-save-v1'
runner.BEFORE = '23d3308077ed3bdfa8e8d7a35f6045914156ab5f'
runner.PREFIXES += ('tools/quality/pg16042_', 'tools/quality/pg16044_', 'tools/quality/pg16046_', 'tools/quality/pg16048_', 'tools/quality/pg16050_', 'tools/quality/pg16052_', 'tools/quality/pg16054_', 'tools/quality/pg16056_', 'tools/quality/architecture/BackupPublicRequestWholeNineJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
