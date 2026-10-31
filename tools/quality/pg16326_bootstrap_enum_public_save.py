"""Exact public enum/source-denominator delta only, never held contents or global G07 claim."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16326-bootstrap-enum-public-save-v1'
save.BEFORE='cfb7fb0ebca5defdd26e53ec37647e2824838e3b'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16312_',
    'tools/quality/pg16314_','tools/quality/pg16316_','tools/quality/pg16317_',
    'tools/quality/pg16318_','tools/quality/pg16320_','tools/quality/pg16322_',
    'tools/quality/pg16324_','tools/quality/pg16326_',
    'tools/quality/architecture/BootstrapEnumOneJunitLauncher.java')

if __name__=='__main__':save.main()
