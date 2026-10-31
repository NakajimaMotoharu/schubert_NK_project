"""Exact public management catch-purpose evidence delta, not whole G07."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16366-management-observation-public-save-v1'
save.BEFORE='f39560c3d51a173d6f9782712dc409d406e361f8'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16362_',
    'tools/quality/pg16364_','tools/quality/pg16366_')

if __name__=='__main__':save.main()
