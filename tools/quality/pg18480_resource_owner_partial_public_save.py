"""Preserve owner-domain partial results at quota stop; no runtime or acceptance claims."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18480-resource-owner-partial-public-save-v1'
save.BEFORE='2aef4e2b45656a89c726064c367628245db7553b'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1847','tools/quality/pg1848')
if __name__=='__main__':save.main()
