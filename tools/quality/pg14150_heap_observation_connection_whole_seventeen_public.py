"""Public17 supplied heap observation, no actual JVM management or global quality claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14150-heap-observation-connection-whole-seventeen-public-v1'
scan.BEFORE = '39dddcaaf8ab72e306f8790147ee532e20568c4a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/HeapObservationCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
