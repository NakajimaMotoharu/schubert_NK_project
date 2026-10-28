"""Explicit current public text delta; no held-tool content access."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12836-exact-registry-public-v1'
scan.BEFORE='b4445e69b22457a44960d1c24ed5fe973ff8586f'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/pg128','tools/quality/architecture/ExactRegistryJunitLauncher.java','tools/quality/architecture/ExactRegistryArtifactCoverageMeasure.java','tools/quality/architecture/ExactRegistryDbCallerJunitLauncher.java','tools/quality/architecture/ExactRegistryDbCallerArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
