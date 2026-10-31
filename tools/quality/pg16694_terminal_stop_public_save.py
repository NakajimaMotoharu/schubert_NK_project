"""Exact original terminal-stop public delta; held paths excluded before metadata/content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16694-terminal-stop-public-save-v1'
save.BEFORE='cf106d40566e4fc0d77efc77a0576b45adde39d3'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16680_','tools/quality/pg16682_','tools/quality/pg16684_','tools/quality/pg16686_','tools/quality/pg16688_','tools/quality/pg16690_','tools/quality/pg16692_','tools/quality/pg16694_')
if __name__=='__main__':save.main()
