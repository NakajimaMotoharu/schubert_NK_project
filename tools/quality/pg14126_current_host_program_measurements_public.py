"""Public provisional host measurement registry/WBS metadata only, no formal promotion."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14126-current-host-program-measurements-public-v1'
scan.BEFORE = '55d0758b1ab88da5e0a10c3a7d75fd3a93b36015'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/current_host_program_measurements_v1.py')

if __name__ == '__main__':scan.main()
