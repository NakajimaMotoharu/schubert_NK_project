"""Exact public original-eight/metadata delta; exclude held files before content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16412-legacy-policy-public-save-v1'
save.BEFORE='77e4d3278fb882a7551e5374b00a3d999b7178ca'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16398_','tools/quality/pg16400_','tools/quality/pg16401_','tools/quality/pg16402_','tools/quality/pg16403_','tools/quality/pg16404_','tools/quality/pg16405_','tools/quality/pg16406_','tools/quality/pg16408_','tools/quality/pg16410_','tools/quality/pg16412_','tools/quality/architecture/LegacyPolicyEightJunitLauncher.java')
if __name__=='__main__':save.main()
