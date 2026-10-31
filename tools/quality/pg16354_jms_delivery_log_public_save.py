"""Exact public six-Source catch-purpose delta, no held file metadata/content or global G07 claim."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16354-jms-delivery-log-public-save-v1'
save.BEFORE='2a183f49e66d85afabadab0ba5b2f1fe251cddc9'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16350_',
    'tools/quality/pg16352_','tools/quality/pg16354_')

if __name__=='__main__':save.main()
