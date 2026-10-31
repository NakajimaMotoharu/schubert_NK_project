"""Public source-bound Expiry24 evidence plus preserved failed writer metadata."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15970-expiry-scope-public-save-v1'
runner.BEFORE = '5f1e7ab848005480b0863cb462f36c3d8e08fc91'
runner.PREFIXES += ('tools/quality/pg159', 'tools/quality/architecture/ExpirySuccessfulScopeTwentyFourJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
