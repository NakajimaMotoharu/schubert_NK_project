"""Public exact delta only, excluding the two held paths before metadata/content access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16024-cleanup-expiry-public-save-v1'
runner.BEFORE = '1edb958353359e3cc80f5549495897aae6a328f1'
runner.PREFIXES += ('tools/quality/pg16010_', 'tools/quality/pg16012_', 'tools/quality/pg16014_', 'tools/quality/pg16016_', 'tools/quality/pg16018_', 'tools/quality/pg16020_', 'tools/quality/pg16022_', 'tools/quality/pg16024_', 'tools/quality/architecture/CleanupExpiryWholeSixteenJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
