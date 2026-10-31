"""Public delta for current joint27; held path exclusion precedes reads."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15986-expiry-joint-public-save-v1'
runner.BEFORE = '6e271b11b6efdedee2a9b9ce032c14a9d712183f'
runner.PREFIXES += ('tools/quality/pg159', 'tools/quality/architecture/ExpiryJdbcJointTwentySevenJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
