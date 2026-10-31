"""Exact public storage group delta only; held files excluded before content/metadata."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16288-storage-attribute-public-save-v1'
save.BEFORE='6393b593e3f3e28b4244b4c977b9a991cdd27809'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16274_',
    'tools/quality/pg16276_','tools/quality/pg16277_','tools/quality/pg16278_',
    'tools/quality/pg16280_','tools/quality/pg16282_','tools/quality/pg16284_',
    'tools/quality/pg16286_','tools/quality/pg16288_')

if __name__=='__main__':save.main()
