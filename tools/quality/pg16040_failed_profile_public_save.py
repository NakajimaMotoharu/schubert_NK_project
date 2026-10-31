"""Public exact delta; existing held paths excluded before file metadata/content access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16040-failed-profile-public-save-v1'
runner.BEFORE = '896bf27179bda65c97730941e4315b03c7e8a32e'
runner.PREFIXES += ('tools/quality/pg16026_', 'tools/quality/pg16028_', 'tools/quality/pg16030_', 'tools/quality/pg16032_', 'tools/quality/pg16034_', 'tools/quality/pg16036_', 'tools/quality/pg16038_', 'tools/quality/pg16040_', 'tools/quality/architecture/FailedProfileWholeSixJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
