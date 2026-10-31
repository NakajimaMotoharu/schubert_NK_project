"""Public primitive-value fixture and metadata delta; held paths excluded before reads."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16002-reference-value-public-save-v1'
runner.BEFORE = '56040e096f1fe01681054f2f7a64a26ba33c13c4'
runner.PREFIXES += ('tools/quality/pg159', 'tools/quality/pg160', 'tools/quality/architecture/RunReferencesTruthTableTest.java', 'tools/quality/architecture/RunReferencesTruthTableJunitLauncher.java')

if __name__ == '__main__':
    runner.main()
