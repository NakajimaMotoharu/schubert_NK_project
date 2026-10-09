"""New-only stage/RO preparation/verify/finite activation; distinct genuine-ISSUED profile."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg864_native.py').read_text().replace('PG864','PG942').replace('Pg864','Pg942').replace('pg864','pg942').replace('0.1.0-PG832','0.1.0-PG862').replace('files98=true','files99=true')
    raw=raw.replace('pg942-frozen-v2.safe.json','pg945-frozen-v1.safe.json').replace("'PG942-compile-v2'","'PG945-compile-v1'").replace('-v2','-v1')
    raw=raw.replace("'genuineParentAccepted':False","'oldGenuineParentProvenanceRequired':True,'newCandidateParentAccepted':False")
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<947 complete genuine-ISSUED dispatch>','exec'),{'__file__':str(R/'pg947_completed_native.py'),'__name__':'__main__'})
