"""Compile only new v2 immutable artifact under same current862 full ABI."""
from pathlib import Path
R=Path(__file__).resolve().parent
def source():return(R/'pg894_compile.py').read_text().replace('from pg894_bootstrap_sources import files,SOURCE','from pg894_sources_v2 import files,SOURCE').replace('pg894-bootstrap-tools-v1','pg894-bootstrap-tools-v2').replace('pg894-frozen-v1','pg894-frozen-v2').replace("'pg894-'+phase+'-v1", "'pg894-'+phase+'-v2")
if __name__=='__main__':exec(compile(source(),'<894 v2 new compile>','exec'),{'__file__':str(R/'pg894_compile_v2.py'),'__name__':'__main__'})
