"""Exact public eight-fixture delta, excluding held paths before metadata."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16096-public-canonical-aad-public-save-v1'
runner.BEFORE = '49b0035714d07eb86bf37a11827e2962662c1cef'
runner.PREFIXES += ('tools/quality/pg16082_', 'tools/quality/pg16084_', 'tools/quality/pg16086_',
                    'tools/quality/pg16088_', 'tools/quality/pg16090_', 'tools/quality/pg16092_',
                    'tools/quality/pg16093_', 'tools/quality/pg16094_', 'tools/quality/pg16096_',
                    'tools/quality/architecture/PublicCanonicalAadValueTest.java',
                    'tools/quality/architecture/PublicCanonicalAadValueJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
