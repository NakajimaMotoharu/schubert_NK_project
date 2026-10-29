"""Seven static ownership references and unchanged WBS semantics; no dynamic qualification."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13952-web-startup-resource-seven-public-v1'
scan.BEFORE = '34aa7a65535879d234962b5497fc7f5ec0c38e46'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/f03_web_startup_resource_seven_trace.py')

if __name__ == '__main__':scan.main()
