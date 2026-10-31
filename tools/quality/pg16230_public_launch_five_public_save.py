"""Exact changed public text save; held names excluded by the qualified three-pattern scanner."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16230-public-launch-five-public-save-v1'
save.BEFORE='89acbb31741a033a917df6c138704351f7a95ead'
save.PREFIXES=('documents/','evidence/01_PT/', 'tools/quality/pg16216_', 'tools/quality/pg16217_',
    'tools/quality/pg16218_', 'tools/quality/pg16219_', 'tools/quality/pg16220_', 'tools/quality/pg16222_',
    'tools/quality/pg16224_', 'tools/quality/pg16226_', 'tools/quality/pg16228_', 'tools/quality/pg16230_',
    'tools/quality/architecture/PublicLaunchFramingBoundaryTest.java',
    'tools/quality/architecture/PublicLaunchFiveJunitLauncher.java',
    'tools/quality/architecture/PublicLaunchValueProbeAuditV1.java')

if __name__=='__main__':save.main()
