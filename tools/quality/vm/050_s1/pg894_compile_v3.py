"""Fresh v3 same current862 ABI; global/body fixtures precede compilation."""
from pathlib import Path
from pg894_compile_v2 import source as previous
R=Path(__file__).resolve().parent
def source():return previous().replace('from pg894_sources_v2 import files,SOURCE','from pg894_sources_v3 import files,SOURCE').replace('pg894-bootstrap-tools-v2','pg894-bootstrap-tools-v3').replace('pg894-frozen-v2','pg894-frozen-v3').replace("'pg894-'+phase+'-v2","'pg894-'+phase+'-v3")
if __name__=='__main__':exec(compile(source(),'<894 v3 new compile>','exec'),{'__file__':str(R/'pg894_compile_v3.py'),'__name__':'__main__'})
