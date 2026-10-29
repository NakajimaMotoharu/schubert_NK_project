"""Public original whole6 memory contracts and explicit partial coverage/unmeasured inventory."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13896-live-intent-fence-public-v1'
scan.BEFORE = '1e66363f5b606ba206c890a6b4cf893d82aa887f'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/LiveIntentFenceMemoryCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
