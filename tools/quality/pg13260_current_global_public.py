"""Finite changed-public-file pattern scan, with held files subtracted before content access."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13260-current-global-public-v1'
scan.BEFORE = '218157ed7ab4b400a360adace63c5e5e8eb5fd87'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132','tools/quality/f03_all_java_auxiliary.py')
if __name__ == '__main__':scan.main()
